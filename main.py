# ! /usr/bin/python
import shutil
from pathlib import Path

import json5

from src.craftables import convert_craftables
from src.dynamic_tokens import get_config_schema, get_dynamic_tokens
# from src.buildings import convert_buildings
from src.foliage import convert_trees

if __name__ == "__main__":
    print("Reading configuration file...")
    with open("config.json", "r", encoding="utf-8") as file:
        config = json5.loads(file.read())
    mod_folder_path = Path(config["mod_folder_path"])
    keywords = config["keywords"]
    print(f"Mod folder: {mod_folder_path}")
    print(f"Keywords to use: {keywords}\n")

    print("Cleaning up Textures/ folder...")
    # clean up after ourselves
    if (mod_folder_path / "Textures").exists():
        shutil.rmtree(mod_folder_path / "Textures")
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
        try:
            if any("weather" in key.lower() for key in change["When"]):
                continue
        except KeyError:
            pass
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


    print(f"Finished conversion. Please check files in {mod_folder_path / 'Textures'}.\n")
    print(f"Converted items: {', '.join(objects_replaced)}")
