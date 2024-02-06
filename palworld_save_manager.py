import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from os.path import expanduser, isdir, splitext, basename, isfile
from configparser import ConfigParser
from save_modifier import replace_save_file, swap_save_file, get_player_list, rename_player, update_host_meta
import tkinter.font as tkFont
import glob
import webbrowser

#region [Base Window]
root = tk.Tk()
root.title("Palworld Save Manager")

root_height  = 600
root_width  = 600

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

center_x = int(screen_width/2 - root_width / 2)
center_y = int(screen_height/2 - root_height / 2)

root.geometry(f'{root_width}x{root_height}+{center_x}+{center_y}')
root.iconbitmap('icon.ico')
#endregion

#region [Setup Path]
#world save
world_frame = ttk.Frame(root)
world_frame.pack(padx=10, pady=5, fill='x', expand=False)

world_save_path = tk.StringVar()

world_save_label = ttk.Label(world_frame, text="world save path")
world_save_label.pack(fill='x', expand=True)

def world_browse_clicked():
	directory = fd.askdirectory(
		title='Select game world folder (Should contain "Players" folder)',
		initialdir=expanduser('~') + '\\AppData\\Local\\Pal\\Saved\\SaveGames'
	)
	if not directory:
		return
	if not isdir(directory + '/Players'):
		messagebox.showerror(title='Wrong folder selected', message='Selected folder must contain "Players" folder')
		return
	world_save_path.set(directory)
	config.set('path', 'world', world_save_path.get())
	save_config()
	refresh_clicked()

world_save_entry = ttk.Entry(world_frame, textvariable=world_save_path)
world_save_entry.pack(fill='x', side='left', expand=True)

world_save_browse_button = ttk.Button(world_frame, text="Browse", command=world_browse_clicked)
world_save_browse_button.pack(side='left')
#endregion

#region [Config Loader]
config = ConfigParser()
config.read('config.ini')

if not config.has_section('path'):
	config.add_section('path')

if not config.has_section('devices'):
	config.add_section('devices')

if config.has_option('path', 'world'):
	world_save_path.set(config.get('path', 'world'))

def save_config():
	with open('config.ini', 'w') as f:
		config.write(f)

#endregion

#region [List Display]
headers = ['Device GUID', 'Device Name', 'Player Name']
player_list = []

browser_frame = ttk.Frame(root)
browser_frame.pack(padx=10, pady= 5, fill='x', expand=False, side='top')

browser_label = ttk.Label(browser_frame, text="Save Files")
browser_label.pack(side='top', fill='x')

def append_meta():
	global player_list
	player_names = get_player_list(world_save_path.get() + "/Level.sav")
	for (i, entry) in enumerate(player_list):
		if entry[0] == '00000000000000000000000000000001':
			player_list[i][1] = 'Host'
		elif config.has_option('devices', entry[0]):
			player_list[i][1] = config.get('devices', entry[0])
		for name in player_names:
			if name[0] == entry[0]:
				player_list[i][2] = name[1]

def refresh_clicked():
	global player_list
	player_list = []
	player_folder_path = world_save_path.get() + "/Players/"

	if not isfile(world_save_path.get() + "/Level.sav") or not isdir(player_folder_path):
		return
	
	box.tree.delete(*box.tree.get_children())
	root.update()

	root.title("Palworld Save Manager (Refreshing, please wait)")
	if isdir(player_folder_path):
		for path in glob.glob(glob.escape(player_folder_path) + "*.sav"):
			player_list.append([splitext(basename(path))[0], '', ''])
	append_meta()
	box._refresh_data()
	clear_meta_editor()
	root.title("Palworld Save Manager")

buttons_frame = ttk.Frame(browser_frame)
buttons_frame.pack(side='top', fill='x')

refresh_button = ttk.Button(buttons_frame, text="Refresh List", command=refresh_clicked)
refresh_button.pack(side='left')

def open_clicked():
	if len(world_save_path.get()) == 0:
		return
	webbrowser.open('file://' + world_save_path.get() + "/Players")

open_button = ttk.Button(buttons_frame, text="Open Folder", command=open_clicked)
open_button.pack(side='left')

browser_wrapper = ttk.Frame(browser_frame, height=150)
browser_wrapper.pack_propagate(False)
browser_wrapper.pack(fill='x', side='top')

class MultiColumnListbox(object):
	def __init__(self):
		self.tree = None
		self._setup_widgets()
		self._build_tree()

	def _refresh_data(self):
		self.container.destroy()
		self.__init__()

	def _setup_widgets(self):
		self.container = ttk.Frame(browser_wrapper)
		self.container.pack(fill='both', expand=True)
		self.tree = ttk.Treeview(columns=headers, show="headings")
		vsb = ttk.Scrollbar(orient="vertical",
			command=self.tree.yview)
		self.tree.configure(yscrollcommand=vsb.set)
		self.tree.grid(column=0, row=0, sticky='nsew', in_=self.container)
		vsb.grid(column=1, row=0, sticky='ns', in_=self.container)
		self.container.grid_columnconfigure(0, weight=1)
		self.container.grid_rowconfigure(0, weight=1)

	def _build_tree(self):
		for col in headers:
			self.tree.heading(col, text=col)
                # command=lambda c=col: sortby(self.tree, c, 0))
			# adjust the column's width to the header string
			self.tree.column(col,
				width=tkFont.Font().measure(col))

		for item in player_list:
			self.tree.insert('', 'end', values=item)
			# # adjust column's width if necessary to fit each value
			for ix, val in enumerate(item):
				col_w = tkFont.Font().measure(val)
				if self.tree.column(headers[ix],width=None)<col_w:
					self.tree.column(headers[ix], width=col_w-30)
		
		self.tree.bind("<ButtonRelease-1>", self._on_click)

	def _on_click(self, event):
		selection = self.tree.selection()
		if len(selection) == 0:
			return
		item = selection[0]
		entry_clicked(self.tree.index(item))

box = MultiColumnListbox()
#endregion

def entry_clicked(index: int):
	guidVar.set(player_list[index][0])
	deviceVar.set(player_list[index][1])
	nameVar.set(player_list[index][2])
	if guidVar.get() == '00000000000000000000000000000001':
		device_entry.config(state='readonly')
	else:
		device_entry.config(state='normal')

	if oldGuidVar.get() == 'Click list to select':
		oldGuidVar.set(player_list[index][0])
		newGuidVar.set('Click list to select')
	elif player_list[index][0] != oldGuidVar.get():
		newGuidVar.set(player_list[index][0])

#region [Swapper]
swapper_frame = ttk.Frame(root)
swapper_frame.pack(padx=10, pady=5, fill='both', expand=True)

# swapper_frame.columnconfigure(3, weight=1)
swapper_frame.columnconfigure(4, weight=1)

swapper_title = ttk.Label(swapper_frame, text="Profile Swapper/Replacer")
swapper_title.grid(row=0, column=0, columnspan=5, sticky='w')

old_guid_label = ttk.Label(swapper_frame, text="Old GUID")
old_guid_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)

oldGuidVar = tk.StringVar()
oldGuidVar.set('Click list to select')

old_guid_entry = ttk.Entry(swapper_frame, state='readonly', textvariable=oldGuidVar)
old_guid_entry.grid(row=1, column=1, columnspan=3, sticky='ew')

# old_guid_explanation = ttk.Label(swapper_frame, text="(Data preserved during replacement)")
old_guid_explanation = ttk.Label(swapper_frame, text="")
old_guid_explanation.grid(row=1, column=4, sticky='w', padx=10, pady=5, columnspan=2)

new_guid_label = ttk.Label(swapper_frame, text="New GUID")
new_guid_label.grid(row=2, column=0, sticky='w', padx=10, pady=5)

newGuidVar = tk.StringVar()

new_guid_entry = ttk.Entry(swapper_frame, state='readonly', textvariable=newGuidVar)
new_guid_entry.grid(row=2, column=1, columnspan=3, sticky='ew')

# new_guid_explanation = ttk.Label(swapper_frame, text="(Data destroyed during replacement)")
new_guid_explanation = ttk.Label(swapper_frame, text="")
new_guid_explanation.grid(row=2, column=4, sticky='w', padx=10, pady=5, columnspan=2)

def reset_pressed():
	oldGuidVar.set('Click list to select')
	newGuidVar.set('')

def replace_pressed():
	hasOld = False
	hasNew = False

	for player in player_list:
		if player[0] == oldGuidVar.get():
			hasOld = True
		elif player[0] == newGuidVar.get():
			hasNew = True

	if not hasOld or not hasNew:
		return

	new_player_name = ''
	old_player_name = ''
	for player in player_list:
		if player[0] == newGuidVar.get():
			new_player_name = player[2]
		elif player[0] == oldGuidVar.get():
			old_player_name = player[2]

	if messagebox.askyesno("Are you sure?", "Operation will DESTROY save data for \n" + new_player_name + " (" + newGuidVar.get() + ")\nand replace it with player data from \n" + old_player_name + " (" + oldGuidVar.get() + ")\n\nProceed?", icon="warning"):
		messagebox.showinfo("", "Process will take about 10-20 seconds to complete.\nProgram will be unresponsive in the meantime")
		root.title("Palworld Save Manager (Replacement in progress, please wait)")
		success = replace_save_file(world_save_path.get(), newGuidVar.get(), oldGuidVar.get())
		if success:
			update_host_meta(world_save_path.get())
		root.title("Palworld Save Manager")
		if success:
			messagebox.showinfo("", "Operation Completed")
			clear_meta_editor()
			refresh_clicked()
			reset_pressed()
		else:
			messagebox.showerror("Something went wrong", "Operation failed, please check console for more info")

def swap_pressed():
	hasOld = False
	hasNew = False

	for player in player_list:
		if player[0] == oldGuidVar.get():
			hasOld = True
		elif player[0] == newGuidVar.get():
			hasNew = True

	if not hasOld or not hasNew:
		return

	new_player_name = ''
	old_player_name = ''
	for player in player_list:
		if player[0] == newGuidVar.get():
			new_player_name = player[2]
		elif player[0] == oldGuidVar.get():
			old_player_name = player[2]
	
	if messagebox.askyesno("Are you sure?", "Operation will swap save data for \n" + new_player_name + " (" + newGuidVar.get() + ") and \n" + old_player_name + " (" + oldGuidVar.get() + ")\n\nProceed?"):
		messagebox.showinfo("", "Process will take about 10-20 seconds to complete.\nProgram will be unresponsive in the meantime")
		root.title("Palworld Save Manager (Swap in progress, please wait)")
		success = swap_save_file(world_save_path.get(), newGuidVar.get(), oldGuidVar.get())
		if success:
			update_host_meta(world_save_path.get())
		root.title("Palworld Save Manager")
		if success:
			root.title("Palworld Save Manager")
			messagebox.showinfo("", "Operation Completed")
			clear_meta_editor()
			refresh_clicked()
			reset_pressed()
		else:
			messagebox.showerror("Something went wrong", "Operation failed, please check console for more info")

swap_button = ttk.Button(swapper_frame, text="Swap", command=swap_pressed)
swap_button.grid(row=3, column=1, sticky='w', pady=5)

replace_button = ttk.Button(swapper_frame, text="Replace", command=replace_pressed)
replace_button.grid(row=3, column=2, sticky='w', pady=5)

reset_button = ttk.Button(swapper_frame, text="Reset", command=reset_pressed)
reset_button.grid(row=3, column=3, sticky='w', padx=5, pady=5)

map_data_label = ttk.Label(swapper_frame, text="Map data is stored locally on device per player")
map_data_label.grid(row=4, column=1, columnspan=5, sticky='w')

map_loc_label = ttk.Label(swapper_frame, text="Transfer LocalData.sav manually to preserve map data")
map_loc_label.grid(row=5, column=1, columnspan=5, sticky='w')

#endregion

#region [Metadata Editor]
meta_editor_frame = ttk.Frame(root)
meta_editor_frame.pack(padx=10, pady= 5, fill='both', expand=True)

meta_editor_frame.columnconfigure(1, weight=1)
meta_editor_frame.columnconfigure(2, weight=1)

editor_title = ttk.Label(meta_editor_frame, text="Metadata Editor")
editor_title.grid(row=0, column=0, columnspan=5, sticky='w')

guid_label = ttk.Label(meta_editor_frame, text="Device GUID")
guid_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)

guidVar = tk.StringVar()

guid_entry = ttk.Entry(meta_editor_frame, state='readonly', textvariable=guidVar)
guid_entry.grid(row=1, column=1, sticky='ew')

device_label = ttk.Label(meta_editor_frame, text="Device Name")
device_label.grid(row=2, column=0, sticky='w', padx=10, pady=5)

deviceVar = tk.StringVar()

device_entry = ttk.Entry(meta_editor_frame, textvariable=deviceVar)
device_entry.grid(row=2, column=1, sticky='ew')

device_explanation = ttk.Label(meta_editor_frame, text="(Convenience only, does not edit save)")
device_explanation.grid(row=2, column=2, sticky='w', padx=10, pady=5, columnspan=2)

name_label = ttk.Label(meta_editor_frame, text="Player Name")
name_label.grid(row=3, column=0, sticky='w', padx=10, pady=5)

nameVar = tk.StringVar()

name_entry = ttk.Entry(meta_editor_frame, textvariable=nameVar)
name_entry.grid(row=3, column=1, sticky='ew')

name_explanation = ttk.Label(meta_editor_frame, text="(Edits save file)")
name_explanation.grid(row=3, column=2, sticky='w', padx=10, pady=5, columnspan=2)

def save_pressed():
	global player_list
	if not guidVar.get():
		return
	if guidVar.get() != '00000000000000000000000000000001':
		config.set('devices', guidVar.get(), deviceVar.get())
		save_config()
		for player in player_list:
			if player[0] == guidVar.get():
				player[1] = deviceVar.get()
		box._refresh_data()

	#Only edit level.sav if name change detected
	for player in player_list:
		if player[0] == guidVar.get():
			if player[2] != nameVar.get():
				if messagebox.askyesno("Are you sure?", "Operation will rename " + player[2] + " to " + nameVar.get()):
					messagebox.showinfo("", "Process will take a few seconds to complete.\nProgram will be unresponsive in the meantime")
					change_player_name(player[0], nameVar.get())
			break

def change_player_name(guid, new_name):
	root.title("Palworld Save Manager (Renaming in progress, please wait)")
	success = rename_player(world_save_path.get(), guid, new_name)
	if success:
		update_host_meta(world_save_path.get())
	root.title("Palworld Save Manager")
	if success:
		messagebox.showinfo("", "Operation Completed")
		refresh_clicked()
	else:
		messagebox.showerror("Something went wrong", "Operation failed, please check console for more info")

def clear_meta_editor():
	guidVar.set('')
	nameVar.set('')
	deviceVar.set('')

save_button = ttk.Button(meta_editor_frame, text="Save", command=save_pressed)
save_button.grid(row=4, column=1, sticky='w', pady=5)	
#endregion

link = tk.Label(root, text="If you found this tool helpful, maybe treat me to a Ko-fi? :)", fg="grey", cursor="hand2")
link.pack(side='bottom', anchor='se', padx=3, pady=3)
link.bind("<Button-1>", lambda e: webbrowser.open_new("https://ko-fi.com/auggust"))

refresh_clicked()
root.mainloop()