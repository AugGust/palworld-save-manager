#!/usr/bin/env python3

import json

from lib.gvas import GvasFile
from lib.noindent import CustomEncoder
from lib.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from lib.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS

def convert_sav_to_json(filename):
	print(f"Decompressing sav file")
	with open(filename, "rb") as f:
		data = f.read()
		raw_gvas, _ = decompress_sav_to_gvas(data)
	gvas_file = GvasFile.read(raw_gvas, PALWORLD_TYPE_HINTS, PALWORLD_CUSTOM_PROPERTIES)
	jsontext = json.dumps(gvas_file.dump(), indent=None, cls=CustomEncoder, ensure_ascii=False)
	return json.loads(jsontext)

def convert_json_to_sav(data, output_path):
	gvas_file = GvasFile.load(data)
	if (
		"Pal.PalWorldSaveGame" in gvas_file.header.save_game_class_name
		or "Pal.PalLocalWorldSaveGame" in gvas_file.header.save_game_class_name
	):
		save_type = 0x32
	else:
		save_type = 0x31
	sav_file = compress_gvas_to_sav(
		gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type
	)
	print(f"Writing SAV file to {output_path}")
	with open(output_path, "wb") as f:
		f.write(sav_file)
