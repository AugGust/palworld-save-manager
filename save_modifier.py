import os
from convert import convert_json_to_sav, convert_sav_to_json
import copy

level_json_cached = None

def rename_player(save_path, player_guid, new_name):
	global level_json_cached

	guid_formatted = '{}-{}-{}-{}-{}'.format(player_guid[:8], player_guid[8:12], player_guid[12:16], player_guid[16:20], player_guid[20:]).lower()
	level_sav_path = save_path + '/Level.sav'

	# save_path must exist in order to use it.
	if not os.path.exists(save_path):
		print('ERROR: Your given <save_path> of "' + save_path + '" does not exist. Did you enter the correct path to your save folder?')
		return False
	
	if not level_json_cached:
		print('ERROR: Please cache level json by refreshing first!')
		return False
	
	characters = level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"]
	for character in characters:
		if "IsPlayer" in character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]:
			if (character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]["IsPlayer"]["value"]):
				if character["key"]["PlayerUId"]["value"] == guid_formatted:
					character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]["NickName"]["value"] = new_name
					break

	level_json = copy.deepcopy(level_json_cached)
	convert_json_to_sav(level_json, level_sav_path)
	
	print('Converted JSON back to save file')	
	print('Renamed! Have fun!')
	return True

def update_host_meta(save_path):
	global level_json_cached

	meta_sav_path = save_path + '/LevelMeta.sav'

	# save_path must exist in order to use it.
	if not os.path.exists(save_path):
		print('ERROR: Your given <save_path> of "' + save_path + '" does not exist. Did you enter the correct path to your save folder?')
		return
	
	if not level_json_cached:
		print('ERROR: Please cache level json by refreshing first!')
		return
	
	if not os.path.isfile(meta_sav_path):
		print('ERROR: LevelMeta does not exist. Did you enter the correct path to your save folder?')
		return
	
	new_host_name = ''
	new_host_level = 0

	characters = level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"]
	for character in characters:
		if "IsPlayer" in character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]:
			if (character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]["IsPlayer"]["value"]):
				if character["key"]["PlayerUId"]["value"].replace('-', '') == '00000000000000000000000000000001':
					new_host_name = character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]["NickName"]["value"]
					new_host_level = character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]["Level"]["value"]
					break

	if not new_host_name:
		return
	
	meta_json = convert_sav_to_json(meta_sav_path)
	print('Converted meta file to JSON')

	meta_json["properties"]["SaveData"]["value"]["HostPlayerName"]["value"] = new_host_name
	meta_json["properties"]["SaveData"]["value"]["HostPlayerLevel"]["value"] = new_host_level

	convert_json_to_sav(meta_json, meta_sav_path)
	print('Converted JSON back to save file')

def replace_save_file(save_path, new_guid, old_guid):
	global level_json_cached

	# Apply expected formatting for the GUID.
	new_guid_formatted = '{}-{}-{}-{}-{}'.format(new_guid[:8], new_guid[8:12], new_guid[12:16], new_guid[16:20], new_guid[20:]).lower()
	old_guid_formatted = '{}-{}-{}-{}-{}'.format(old_guid[:8], old_guid[8:12], old_guid[12:16], old_guid[16:20], old_guid[20:]).lower()

	level_sav_path = save_path + '/Level.sav'
	old_sav_path = save_path + '/Players/'+ old_guid + '.sav'
	new_sav_path = save_path + '/Players/' + new_guid + '.sav'
	
	# save_path must exist in order to use it.
	if not os.path.exists(save_path):
		print('ERROR: Your given <save_path> of "' + save_path + '" does not exist. Did you enter the correct path to your save folder?')
		return False
	
	# The player needs to have created a character on the dedicated server and that save is used for this script.
	if not os.path.exists(new_sav_path):
		print('ERROR: Your player save does not exist. Did you enter the correct new GUID of your player? It should look like "8E910AC2000000000000000000000000".\nDid your player create their character with the provided save? Once they create their character, a file called "' + new_sav_path + '" should appear. Look back over the steps in the README on how to get your new GUID.')
		return False
	
	if not level_json_cached:
		print('ERROR: Please cache level json by refreshing first!')
		return False

	# Convert save files to JSON so it is possible to edit them.
	old_json = convert_sav_to_json(old_sav_path)
	new_json = convert_sav_to_json(new_sav_path)
	print('Converted save files to JSON')
	
	# Replace all instances of the old GUID with the new GUID.
	
	# Player data replacement.
	old_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"] = new_guid_formatted
	old_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["PlayerUId"]["value"] = new_guid_formatted
	old_instance_id = old_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]

	# Level data replacement.
	new_instance_id = new_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]

	instance_ids_len = len(level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"])
	# Delete "New" Player ID entry
	for i in range(instance_ids_len):
		instance_id = level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["InstanceId"]["value"]
		if instance_id == new_instance_id:
			level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"].pop(i)
			break
	
	instance_ids_len = len(level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"])
	for i in range(instance_ids_len):
		instance_id = level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["InstanceId"]["value"]
		if instance_id == old_instance_id:
			level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["PlayerUId"]["value"] = new_guid_formatted

	# Guild data replacement.
	group_ids_len = len(level_json_cached["properties"]["worldSaveData"]["value"]["GroupSaveDataMap"]["value"])
	for i in range(group_ids_len):
		group_id = level_json_cached["properties"]["worldSaveData"]["value"]["GroupSaveDataMap"]["value"][i]
		if group_id["value"]["GroupType"]["value"]["value"] == "EPalGroupType::Guild":
			character_handle_len = len(group_id["value"]["RawData"]["value"]["individual_character_handle_ids"])
			for j in range(character_handle_len):
				if group_id["value"]["RawData"]["value"]["individual_character_handle_ids"][j]["guid"] == old_guid_formatted:
					group_id["value"]["RawData"]["value"]["individual_character_handle_ids"][j]["guid"] = new_guid_formatted

			players_len = len(group_id["value"]["RawData"]["value"]["players"])
			for j in range(players_len):
				if group_id["value"]["RawData"]["value"]["players"][j]["player_uid"] == old_guid_formatted:
					group_id["value"]["RawData"]["value"]["players"][j]["player_uid"] = new_guid_formatted
	print('Changes have been made')
	
	convert_json_to_sav(old_json, old_sav_path)
	level_json = copy.deepcopy(level_json_cached)
	convert_json_to_sav(level_json, level_sav_path)
	print('Converted JSON back to save files')
	
	# We must rename the patched save file from the old GUID to the new GUID for the server to recognize it.
	if os.path.exists(new_sav_path):
		os.remove(new_sav_path)
	os.rename(old_sav_path, new_sav_path)
	print('Fix has been applied! Have fun!')
	return True

def swap_save_file(save_path, a_guid, b_guid):
	global level_json_cached
	# Apply expected formatting for the GUID.
	b_new_guid_formatted = '{}-{}-{}-{}-{}'.format(a_guid[:8], a_guid[8:12], a_guid[12:16], a_guid[16:20], a_guid[20:]).lower()
	a_new_guid_formatted = '{}-{}-{}-{}-{}'.format(b_guid[:8], b_guid[8:12], b_guid[12:16], b_guid[16:20], b_guid[20:]).lower()
	
	level_sav_path = save_path + '/Level.sav'
	a_sav_path = save_path + '/Players/' + a_guid + '.sav'
	b_sav_path = save_path + '/Players/'+ b_guid + '.sav'
	temp_sav_path = save_path + '/Players/temp.sav'
	
	# save_path must exist in order to use it.
	if not os.path.exists(save_path):
		print('ERROR: Your given <save_path> of "' + save_path + '" does not exist. Did you enter the correct path to your save folder?')
		return False
	
	# The player needs to have created a character on the dedicated server and that save is used for this script.
	if not os.path.exists(a_sav_path):
		print('ERROR: Your player save does not exist. Did you enter the correct new GUID of your player? It should look like "8E910AC2000000000000000000000000".\nDid your player create their character with the provided save? Once they create their character, a file called "' + a_sav_path + '" should appear. Look back over the steps in the README on how to get your new GUID.')
		return False
	
	if not os.path.exists(b_sav_path):
		print('ERROR: Your player save does not exist. Did you enter the correct new GUID of your player? It should look like "8E910AC2000000000000000000000000".\nDid your player create their character with the provided save? Once they create their character, a file called "' + a_sav_path + '" should appear. Look back over the steps in the README on how to get your new GUID.')
		return False
	
	if not level_json_cached:
		print('ERROR: Please cache level json by refreshing first!')
		return False

	# Convert save files to JSON so it is possible to edit them.
	a_json = convert_sav_to_json(a_sav_path)
	b_json = convert_sav_to_json(b_sav_path)
	print('Converted save files to JSON')

	# Replace all instances of the old GUID with the new GUID.
	
	# Player data replacement.
	a_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"] = a_new_guid_formatted
	a_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["PlayerUId"]["value"] = a_new_guid_formatted
	a_old_instance_id = a_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]

	b_json["properties"]["SaveData"]["value"]["PlayerUId"]["value"] = b_new_guid_formatted
	b_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["PlayerUId"]["value"] = b_new_guid_formatted
	b_old_instance_id = b_json["properties"]["SaveData"]["value"]["IndividualId"]["value"]["InstanceId"]["value"]
	
	# Level data replacement.
	instance_ids_len = len(level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"])
	for i in range(instance_ids_len):
		instance_id = level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["InstanceId"]["value"]
		if instance_id == a_old_instance_id:
			level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["PlayerUId"]["value"] = a_new_guid_formatted
		elif instance_id == b_old_instance_id:
			level_json_cached["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"][i]["key"]["PlayerUId"]["value"] = b_new_guid_formatted
	
	# Guild data replacement.
	group_ids_len = len(level_json_cached["properties"]["worldSaveData"]["value"]["GroupSaveDataMap"]["value"])
	for i in range(group_ids_len):
		group_id = level_json_cached["properties"]["worldSaveData"]["value"]["GroupSaveDataMap"]["value"][i]
		if group_id["value"]["GroupType"]["value"]["value"] == "EPalGroupType::Guild":
			character_handle_len = len(group_id["value"]["RawData"]["value"]["individual_character_handle_ids"])
			for j in range(character_handle_len):
				if group_id["value"]["RawData"]["value"]["individual_character_handle_ids"][j]["guid"] == a_new_guid_formatted:
					group_id["value"]["RawData"]["value"]["individual_character_handle_ids"][j]["guid"] = b_new_guid_formatted
				elif group_id["value"]["RawData"]["value"]["individual_character_handle_ids"][j]["guid"] == b_new_guid_formatted:
					group_id["value"]["RawData"]["value"]["individual_character_handle_ids"][j]["guid"] = a_new_guid_formatted

			players_len = len(group_id["value"]["RawData"]["value"]["players"])
			for j in range(players_len):
				if group_id["value"]["RawData"]["value"]["players"][j]["player_uid"] == a_new_guid_formatted:
					group_id["value"]["RawData"]["value"]["players"][j]["player_uid"] = b_new_guid_formatted
				elif group_id["value"]["RawData"]["value"]["players"][j]["player_uid"] == b_new_guid_formatted:
					group_id["value"]["RawData"]["value"]["players"][j]["player_uid"] = a_new_guid_formatted
	print('Changes have been made')

	convert_json_to_sav(a_json, a_sav_path)
	convert_json_to_sav(b_json, b_sav_path)
	level_json = copy.deepcopy(level_json_cached)
	convert_json_to_sav(level_json, level_sav_path)
	print('Converted JSON back to save files')
	
	# Swap the file names
	os.rename(a_sav_path, temp_sav_path)
	os.rename(b_sav_path, a_sav_path)
	os.rename(temp_sav_path, b_sav_path)
	print('Profiles have been swapped! Have fun!')
	return True

def get_player_list(file, cacheJson: bool = True):
	global level_json_cached
	level_json = convert_sav_to_json(file)
	players = []
	characters = level_json["properties"]["worldSaveData"]["value"]["CharacterSaveParameterMap"]["value"]
	for character in characters:
		if "IsPlayer" in character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]:
			if (character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]["IsPlayer"]["value"]):
				players.append((character["key"]["PlayerUId"]["value"].replace('-','').upper(), character["value"]["RawData"]["value"]["object"]["SaveParameter"]["value"]["NickName"]["value"]))

	if cacheJson:
		level_json_cached = level_json

	return players
