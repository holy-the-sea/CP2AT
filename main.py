# ! /usr/bin/python
import shutil
from pathlib import Path
import os

import json5

from src.craftables import convert_craftables
from src.dynamic_tokens import get_config_schema, get_dynamic_tokens
# from src.buildings import convert_buildings
from src.foliage import convert_trees
from src.furniture import convert_furniture
from src.generate_jsons import generate_new_manifest

if __name__ == "__main__":
    print("Reading configuration file...")
    with open("config.json", "r", encoding="utf-8") as file:
        config = json5.loads(file.read())
    mod_folder_path = config["mod_folder_path"]
    if "[CP]" in mod_folder_path:
        AT_folder_path = Path(mod_folder_path.replace("[CP]", "[AT]"))
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
        if "tilesheets/craftables" in target:  # or "maps/springobjects" in target:
            objects_replaced = convert_craftables(
                change,
                mod_folder_path,
                config_schema_options,
                dynamic_tokens,
                keywords,
                objects_replaced,
            )
        # elif "buildings" in target:
        #     objects_replaced = convert_buildings(
        #         change,
        #         mod_folder_path,
        #         config_schema_options,
        #         dynamic_tokens,
        #         keywords,
        #         objects_replaced
        #     )
        elif "tree" in target:
            objects_replaced = convert_trees(
                change,
                mod_folder_path,
                config_schema_options,
                dynamic_tokens,
                keywords,
                objects_replaced
            )
        elif "furniture" in target:
            objects_replaced = convert_furniture(
                change,
                mod_folder_path,
                config_schema_options,
                dynamic_tokens,
                keywords,
                objects_replaced
            )
        print()

    print("Creating new manifest...")
    generate_new_manifest(mod_folder_path, AT_folder_path)
    print("Done.\n")

    print("Moving files...")
    shutil.move(mod_folder_path / "Textures", AT_folder_path)
    print("Done.\n")

    print(f"Converted items: {', '.join(objects_replaced)}\n")
    print(f"Finished conversion. Please check files in {AT_folder_path}.\n")
