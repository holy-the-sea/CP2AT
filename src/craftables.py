#! /usr/bin/python

import os
import re
from pathlib import Path

import json5
from PIL import Image, ImageChops
from src.file_names import get_file_path
from src.file_variations import get_file_variations, expand_target_variations
from src.texture_json import generate_texture_json

# TODO: do springobjects.png


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
    craftable_objects_info = {
        (value["X"], value["Y"]): {
            "Object": key,
            "Height": value["Height"],
            "Width": value["Width"],
        }
        for key, value in craftable_objects_info.items()
    }

    file = change["FromFile"]
    target_file = Path(change["Target"].lower()).with_suffix(".png")

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
        object_name = craftable_objects_info[(tilesheet_X, tilesheet_Y)]["Object"]
        if object_name == "Campfire_1":
            object_name = "Cookout Kit"
        print(f"Item replacement known: {object_name}")
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
            x in file for x in ["spring", "summer", "fall", "winter"]
        ):
            file_season = (
                re.search(r"(spring|summer|fall|winter)", file).group(1).capitalize()
            )
        else:
            file_season = False

        if "object_name" in locals():
            new_file_path = get_file_path(
                file, object_name, mod_folder_path, file_season
            )
            # * asset is an individual sprite
            if "FromArea" not in change:
                im.save(new_file_path)
                image_variations.append(im)
            # * asset was a tilesheet
            else:
                X = change["FromArea"]["X"]
                Y = change["FromArea"]["Y"]
                width = change["FromArea"]["Width"]
                height = change["FromArea"]["Height"]
                X_right = X + width
                Y_bottom = Y + height
                im = im.crop((X, Y, X_right, Y_bottom))
                im.save(new_file_path)
                image_variations.append(im)
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
        else:
            print("Trying to identify...")
            for coords, values in craftable_objects_info.items():
                object_name = values["Object"]
                if object_name == "Campfire_1":
                    object_name = "Cookout Kit"
                width = values["Width"]
                height = values["Height"]

                im_vanilla = Image.open(target_file).convert("RGB")
                X, Y = [*coords]
                X_right = X + width
                Y_bottom = Y + height
                im_cropped_vanilla = im_vanilla.crop((X, Y, X_right, Y_bottom))

                im_mod = Image.open(mod_folder_path / file).convert("RGB")
                im_cropped_mod = im_mod.crop((X, Y, X_right, Y_bottom))

                diff = ImageChops.difference(im_cropped_vanilla, im_cropped_mod)
                if diff.getbbox() is not None:  # got a hit
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
