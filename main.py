# ! /usr/bin/python
import shutil
from pathlib import Path, PurePath
from os import path
import os
import re

import json5

from src.craftables import convert_craftables
from src.fences import convert_fences
from src.dynamic_tokens import get_config_schema, get_dynamic_tokens
from src.buildings import convert_buildings
from src.foliage import convert_trees
from src.furniture import convert_furniture
from src.animals import convert_animals
from src.generate_jsons import generate_new_manifest

if __name__ == "__main__":
    print("Reading configuration file...")
    with open("config.json", "r", encoding="utf-8") as file:
        config = json5.loads(file.read())
    mod_folder_path = config["mod_folder_path"]
    if 'output_folder_path' in config:
        AT_folder_path = Path(config['output_folder_path'])
    else:
        if "[CP]" in mod_folder_path:
            AT_folder_path = Path(mod_folder_path.replace("[CP]", "[AT]"))
        else:
            if os.path.sep in mod_folder_path:
                last_elem = PurePath(mod_folder_path).name
                last_elem = f"[AT] {last_elem}"
                mod_folder_path = PurePath(mod_folder_path).parent 
                AT_folder_path = Path(os.path.join(mod_folder_path, last_elem))
            else:
                AT_folder_path = Path(f"[AT] {mod_folder_path}")
    mod_folder_path = Path(mod_folder_path)
    keywords = config["keywords"]
    print(f"Mod folder: {mod_folder_path}")
    print(f"Keywords to use: {keywords}\n")

    print("Cleaning up Textures/ folder...")
    # clean up after ourselves
    if (mod_folder_path / "Textures").exists():
        shutil.rmtree(mod_folder_path / "Textures")
    print("Done.\n")

    print("Making AT folder...")
    if AT_folder_path.exists():
        shutil.rmtree(AT_folder_path)
        os.makedirs(AT_folder_path)
        # os.makedirs(AT_folder_path / "Textures")
    if not (AT_folder_path).exists():
        os.makedirs(AT_folder_path)
        # os.makedirs(AT_folder_path / "Textures")
    print("Done.\n")

    print("Loading content.json...")
    content_json_path = mod_folder_path / "content.json"
    with open(content_json_path, encoding="utf-8") as json_file:
        content_json = json5.loads(json_file.read())
    print("Done.\n")

    # check for ConfigSchema and DynamicTokens
    print("Checking for ConfigSchema and DynamicTokens...")
    config_schema_options = get_config_schema(content_json)
    dynamic_tokens = get_dynamic_tokens(content_json)
    print("Done.\n")

    # start going through changes in content.json
    print("Begin finding changes...\n")
    objects_replaced = {}
    for change in content_json["Changes"]:
        if "Update" in change.keys():
            continue
        try:
            if "DayEvent" in change["When"].keys():
                continue
        except KeyError:
            pass
        #TODO: fix weather-specific skins?
        try:
            if any("weather" in key.lower() for key in change["When"]):
                continue
        except KeyError:
            pass
        #TODO: paste overlay images to create another texture
        try:
            if change["PatchMode"] == "Overlay":
                continue
        except KeyError:
            pass

        target = change["Target"].lower()
        if "," in target:
            target_list = re.sub(",", ".png,", target.title())
            target_list = re.split(r",\s?", target_list)
            change_list = []
            for content in target_list:
                change_copy = change.copy()
                change_copy["Target"] = content
                change_list.append(change_copy)
        else:
            change_list = [change]
        for item in change_list:
            target = item["Target"].lower()
            if "tilesheets/craftables" in target:  # or "maps/springobjects" in target:
                objects_replaced = convert_craftables(
                    item,
                    mod_folder_path,
                    config_schema_options,
                    dynamic_tokens,
                    keywords,
                    objects_replaced,
                )
            elif "fence" in target:
                objects_replaced = convert_fences(
                    item,
                    mod_folder_path,
                    config_schema_options,
                    dynamic_tokens,
                    keywords,
                    objects_replaced
                )
            elif "buildings" in target:
                objects_replaced = convert_buildings(
                    item,
                    mod_folder_path,
                    config_schema_options,
                    dynamic_tokens,
                    keywords,
                    objects_replaced
                )
            elif "tree" in target:
                objects_replaced = convert_trees(
                    item,
                    mod_folder_path,
                    config_schema_options,
                    dynamic_tokens,
                    keywords,
                    objects_replaced
                )
            elif "furniture" in target and "front" not in target:
                objects_replaced = convert_furniture(
                    item,
                    mod_folder_path,
                    config_schema_options,
                    dynamic_tokens,
                    keywords,
                    objects_replaced
                )
            elif "furniturefront" in target:
                continue
            elif "animals" in target:
                objects_replaced = convert_animals(
                    item,
                    mod_folder_path,
                    config_schema_options,
                    dynamic_tokens,
                    keywords,
                    objects_replaced
                )
            else:
                print(f"Not Implemented: {target}")
            print()

    print("Creating new manifest...")
    generate_new_manifest(mod_folder_path, AT_folder_path)
    print("Done.\n")

    print("Moving files...")
    print(f"Moving content.json... {mod_folder_path}")
    mod_folder_textures_path = path.join(mod_folder_path, "Textures")
    shutil.move(mod_folder_textures_path, AT_folder_path)
    print("Done.\n")

    print(f"Converted items: {', '.join(objects_replaced)}\n")
    print(f"Finished conversion. Please check files in {AT_folder_path}.\n")
