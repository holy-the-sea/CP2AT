#! /usr/bin/python

import os
import re
from pathlib import Path

import json5
import numpy as np
from PIL import Image, ImageChops

from src.file_names import (expand_target_variations, get_file_path,
                            get_file_variations)
from src.generate_jsons import generate_texture_json


def split_craftables_replacement(
    tilesheet_coords, dimension_name, craftable_objects_info
):
    tilesheet_X = tilesheet_coords["X"]
    tilesheet_Y = tilesheet_coords["Y"]
    section_width = tilesheet_coords["Width"]
    sprite_X = tilesheet_X
    if dimension_name == "Width":
        object_list = []
        while tilesheet_X <= sprite_X < tilesheet_X + section_width:
            if (sprite_X, tilesheet_Y) not in craftable_objects_info.keys():
                sprite_X += 16
            else:
                object_list.append(
                    craftable_objects_info[(sprite_X, tilesheet_Y)]["Object"]
                )
                sprite_X += 16
        return object_list
    if dimension_name == "Height":
        raise NotImplementedError("lol i don't even know gl hf")


def convert_craftables(
    change,
    mod_folder_path,
    config_schema_options,
    dynamic_tokens,
    keywords,
    objects_replaced,
):

    with open(
        Path(os.getcwd()) / "src/coords_info/craftable_coords.json",
        "r",
        encoding="utf-8",
    ) as json_file:
        craftable_objects_info = json5.loads(json_file.read())
    craftable_coords_info = {
        (value["X"], value["Y"]): {
            "Object": key,
            "Height": value["Height"],
            "Width": value["Width"],
        }
        for key, value in craftable_objects_info.items()
    }

    file = change["FromFile"]
    target_file = Path(change["Target"]).with_suffix(".png")

    found_placeholders = re.findall(r"{{(.*?)}}", file)
    found_seasons = False
    file_season = False

    image_variations = []

    # * no placeholders found in filename
    # * so we're gucci
    if not found_placeholders:
        file_variations = [file]
    # * rip time to start permutations of the name options
    elif found_placeholders:
        file_variations, found_seasons = get_file_variations(
            file,
            mod_folder_path,
            found_placeholders,
            config_schema_options,
            dynamic_tokens,
        )
    file_variations = expand_target_variations(
        file_variations,
        target_file,
        mod_folder_path,
        config_schema_options,
        dynamic_tokens,
    )

    # * check for whole tilesheet replacement
    if "ToArea" in change:
        tilesheet_coords = change["ToArea"]
        tilesheet_X = tilesheet_coords["X"]
        tilesheet_Y = tilesheet_coords["Y"]
        try:
            replacement_width = craftable_coords_info[(tilesheet_X, tilesheet_Y)][
                "Width"
            ]
            replacement_height = craftable_coords_info[(tilesheet_X, tilesheet_Y)][
                "Height"
            ]
            object_name = craftable_coords_info[(tilesheet_X, tilesheet_Y)]["Object"]
            if object_name == "Campfire_1":
                object_name = "Cookout Kit"
            print(f"Item replacement known: {object_name}")
            object_list = [object_name]
            if (
                tilesheet_coords["Width"] != replacement_width
                or tilesheet_coords["Height"] != replacement_height
            ):
                print("Consecutive objects in X-direction replaced, splitting...")
                object_list = split_craftables_replacement(
                    tilesheet_coords, "Width", craftable_coords_info
                )
        except KeyError:
            print(
                f"Couldn't find an object with the coordinates ({tilesheet_X}, {tilesheet_Y})"
            )
            return objects_replaced
    else:
        print(
            "Item names not found from content.json, must do object identification by comparing sprites instead"
        )

    for file in file_variations:
        if re.search("{{.*?}}", file):
            continue
        im = Image.open(mod_folder_path / file)

        # * check if seasonal variations
        if found_seasons or any(
            x in file.lower() for x in ["spring", "summer", "fall", "winter"]
        ):
            file_season = (
                re.search(r"(spring|summer|fall|winter)", file).group(1).capitalize()
            )
        else:
            file_season = False

        if "object_list" in locals():
            for object_name in object_list:
                new_file_path = get_file_path(
                    file, object_name, mod_folder_path, file_season
                )
                # * asset is an individual sprite
                if "FromArea" not in change:
                    im.save(new_file_path)
                    image_variations.append(im)
                # * asset was a tilesheet
                else:
                    if change["FromArea"]["Height"] == im.height and change["FromArea"]["Width"] == im.width:
                        im.save(new_file_path)
                        image_variations.append(im)
                    else:
                        X = craftable_objects_info[object_name]["X"]
                        Y = craftable_objects_info[object_name]["Y"]
                        width = craftable_objects_info[object_name]["Width"]
                        height = craftable_objects_info[object_name]["Height"]
                        X_right = X + width
                        Y_bottom = Y + height
                        im_cropped = im.crop((X, Y, X_right, Y_bottom))
                        im_cropped.save(new_file_path)
                        image_variations.append(im_cropped)
                        print(f"Cropped {object_name} from {Path(file)}.")
                # * update list of which objects we have replaced
                objects_replaced[object_name] = image_variations
                texture_json_path = Path(new_file_path).parent / "texture.json"
                generate_texture_json(
                    texture_json_path,
                    object_name,
                    "Craftable",
                    16,
                    32,
                    keywords,
                    file_season,
                )
        else:
            print("Trying to identify...")
            for coords, values in craftable_coords_info.items():
                object_name = values["Object"]
                if object_name == "Campfire_1":
                    object_name = "Cookout Kit"
                object_width = values["Width"]
                object_height = values["Height"]

                X, Y = [*coords]
                X_right = X + object_width
                Y_bottom = Y + object_height

                im_vanilla = Image.open(target_file).convert("RGBA")
                background = Image.new("RGBA", im_vanilla.size, "white")
                background.paste(im_vanilla, (0, 0), im_vanilla)
                im_vanilla = background
                im_cropped_vanilla = im_vanilla.crop((X, Y, X_right, Y_bottom))

                im_mod = Image.open(mod_folder_path / file).convert("RGBA")
                background = Image.new("RGBA", im_mod.size, "white")
                background.paste(im_mod, (0, 0), im_mod)
                im_mod = background
                im_cropped_mod = im_mod.crop((X, Y, X_right, Y_bottom))

                diff = ImageChops.difference(im_cropped_vanilla, im_cropped_mod)
                if diff.getbbox() is None and np.sum(np.array(diff.getdata())) < 5000:
                    continue
                if sorted(im_cropped_vanilla.getcolors(1024)) != sorted(im_cropped_mod.getcolors(1024)):  # got a hit
                    # make sure it's not just random transparent pi
                    mod_colors = sorted(x for x in im_cropped_mod.getcolors(1024))
                    mod_transparencies = [x[3] for _, x in mod_colors]
                    # mod image has no solid pixels
                    if all(x != 255 for x in mod_transparencies):
                        continue
                    # mod is (mostly) all black image
                    if all(all(x > 250 for x in y[:2]) for _, y in mod_colors):
                        continue
                    # mod is (mostly) all white image
                    if all(all(x < 5 for x in y[:2]) for _, y in mod_colors):
                        continue
                    print(f"Found a match: {object_name} from {Path(file)}...")
                    im_vanilla = Image.open(target_file)
                    im_mod = Image.open(mod_folder_path / file)
                    im_cropped_vanilla = im_vanilla.crop((X, Y, X_right, Y_bottom))
                    im_cropped_mod = im_mod.crop((X, Y, X_right, Y_bottom))
                    new_file_path = get_file_path(
                        file, object_name, mod_folder_path, file_season
                    )
                    im_cropped_mod.save(new_file_path)
                    image_variations.append(im_cropped_mod)
                    print(f"Cropped {object_name} from {Path(file)}.\n")

                    # * update list of which objects we have replaced
                    objects_replaced[object_name] = image_variations
                    texture_json_path = Path(new_file_path).parent / "texture.json"
                    generate_texture_json(
                        texture_json_path,
                        object_name,
                        "Craftable",
                        16,
                        32,
                        keywords,
                        file_season,
                    )
    return objects_replaced
