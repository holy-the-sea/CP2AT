#! /usr/bin/python

import json
import re

import json5


def generate_texture_json(texture_json_path, item_name, item_type, width, height, keywords, file_season):
    try:
        item_name = re.sub(r"_\d+", "", item_name)
        with open(texture_json_path, "r", encoding="utf-8") as json_file:
            old_texture_json = json5.loads(json_file.read())
        old_texture_json["Variations"] += 1
        with open(texture_json_path, "w", encoding="utf-8") as json_file:
            json.dump(old_texture_json, json_file, indent=4)
    except FileNotFoundError:
        texture_json = {}
        texture_json["ItemName"] = item_name
        texture_json["Type"] = item_type
        if file_season:
            texture_json["Seasons"] = [file_season]
        texture_json["TextureWidth"] = width
        texture_json["TextureHeight"] = height
        texture_json["Keywords"] = keywords
        texture_json["Variations"] = 1
        with open(texture_json_path, "w", encoding="utf-8") as json_file:
            json.dump(texture_json, json_file, indent=4)
