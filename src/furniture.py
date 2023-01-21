#! /usr/bin/python

import os
import re
from pathlib import Path

import json5
import numpy as np
from PIL import Image

from src.file_names import get_file_path, get_file_variations, expand_target_variations
from src.generate_jsons import generate_texture_json


def split_replacement(
    tilesheet_coords,
    dimension_name,
    furniture_coords,
    furniture_coords_info,
):
    tilesheet_X = tilesheet_coords["X"]
    tilesheet_Y = tilesheet_coords["Y"]
    section_width = tilesheet_coords["Width"]
    if dimension_name == "Width":
        object_list = []
        slice_indices = np.argwhere(furniture_coords[:, 1] == tilesheet_Y)
        for sprite in furniture_coords[slice_indices.ravel()]:
            if tilesheet_X <= sprite[0] < tilesheet_X + section_width:
                furniture_object_data = furniture_coords_info[sprite[0], sprite[1]]
                object_list.append(furniture_object_data["Object"])
        return object_list

    if dimension_name == "Height":
        raise NotImplementedError("lol i don't even know gl hf")


def convert_furniture(
    change,
    mod_folder_path,
    config_schema_options,
    dynamic_tokens,
    keywords,
    objects_replaced,
):
    with open(
        Path(os.getcwd()) / "src/coords_info/furniture_coords.json",
        "r",
        encoding="utf-8",
    ) as json_file:
        furniture_objects_info = json5.loads(json_file.read())
    furniture_coords_info = {
        (value["X"], value["Y"]): {
            "Object": key,
            "Type": value["Type"],
            "Width": value["Width"],
            "Height": value["Height"],
        }
        for key, value in furniture_objects_info.items()
    }
    furniture_coords = np.array(list(furniture_coords_info.keys()))

    file = change["FromFile"]
    target_file = Path(change["Target"].lower()).with_suffix(".png")

    found_placeholders = re.findall(r"{{(.*?)}}", file)
    file_season = False

    object_list = []
    image_variations = []

    # * no placeholders found in filename
    # * so we're gucci
    if not found_placeholders:
        file_variations = [file]
    # * rip time to start permutations of the name options
    elif found_placeholders:
        file_variations, _ = get_file_variations(
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
            width = furniture_coords_info[(tilesheet_X, tilesheet_Y)]["Width"]
        except KeyError:
            print(
                f"Couldn't find an object with the coordinates ({tilesheet_X}, {tilesheet_Y})"
            )
            return objects_replaced
        height = furniture_coords_info[(tilesheet_X, tilesheet_Y)]["Height"]

        if tilesheet_coords["Width"] != width or tilesheet_coords["Height"] != height:
            print("Consecutive objects in X-direction replaced, splitting...")
            object_section_list = split_replacement(
                tilesheet_coords, "Width", furniture_coords, furniture_coords_info
            )
            print(f"Item replacement(s) known: {', '.join(object_section_list)}")
            object_list.extend(object_section_list)
        else:
            object_name = furniture_coords_info[tilesheet_X, tilesheet_Y]["Object"]
            print(f"Object replacement known: {object_name}")
            object_list.append(object_name)

    else:
        print(
            "Item names not found from content.json, must do object identification by comparing sprites instead"
        )
        print("I actually cannot do this yet")
    for file in file_variations:
        if re.search("{{.*?}}", file):
            continue
        im = Image.open(mod_folder_path / file)
        for object_name in object_list:
            data = furniture_objects_info[object_name]
            X = data["X"]
            Y = data["Y"]
            object_width = data["Width"]
            object_height = data["Height"]
            object_type = data["Type"]
            X_right = X + object_width
            Y_bottom = Y + object_height
            new_file_path = get_file_path(
                file, object_name, mod_folder_path, file_season
            )

            im_object = im.crop((X, Y, X_right, Y_bottom))
            if object_type == "rug":
                im_merge = Image.new(
                    "RGBA", (im_object.width, im_object.height), (0, 0, 0, 0)
                )
                im_part1 = im_object.crop(
                    (0, 0, im.width * (3 / 5), im.height * (2 / 3))
                )
                im_part2 = im_object.crop(
                    (im_object.width * (3 / 5), 0, im_object.width, im_object.height)
                )
                im_merge.paste(im_part1, (0, 0))
                im_merge.paste(im_part2, (im_part1.width, 0))
                im_merge.save(new_file_path)
                image_variations.append(im_merge)
            elif object_name == "Large Brown Couch":
                im_merge = Image.new("RGBA", (im.width, im.height), (0, 0, 0, 0))
                im1 = im.crop((0, 0, width * (4 / 3), height))
                im2 = im.crop((im1.width, 0, width * 2, im.height))
                im3 = im.crop((im1.width + im2.width, 0, im.width, height))
                im_merge.paste(im1, (0, 0))
                im_merge.paste(im2, (im1.width, 0))
                im_merge.paste(im3, (im1.width + im2.width, 0))
                im_merge.save(new_file_path)
                image_variations.append(im_merge)
            else:
                im_object.save(new_file_path)
                image_variations.append(im_object)
            objects_replaced[object_name] = image_variations
            print(f"Cropped {object_name} from {Path(file)}.")

            # * add json
            texture_json_path = Path(new_file_path).parent / "texture.json"
            generate_texture_json(
                texture_json_path,
                object_name,
                "Furniture",
                int(object_width),
                int(object_height),
                keywords,
                file_season,
            )

    return objects_replaced
