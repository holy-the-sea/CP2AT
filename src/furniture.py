#! /usr/bin/python

import os
import re
from pathlib import Path

import json5
import json
import numpy as np
from PIL import Image, ImageChops

from src.file_names import (expand_target_variations, get_file_path,
                            get_file_variations)
from src.generate_jsons import generate_texture_json

# load the furniture json bc it's huge
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
        "Rotations": value["Rotations"]
    }
    for key, value in furniture_objects_info.items()
}
furniture_coords = np.array(list(furniture_coords_info.keys()))

def split_replacement(
    tilesheet_coords,
    dimension_name
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


def merge_rug_sprites(im_object):
    im_merge = Image.new("RGBA", (im_object.width, im_object.height), (0, 0, 0, 0))
    im_part1 = im_object.crop(
        (0, 0, im_object.width * (3 / 5), im_object.height * (2 / 3))
    )
    im_part2 = im_object.crop(
        (im_object.width * (3 / 5), 0, im_object.width, im_object.height)
    )
    im_merge.paste(im_part1, (0, 0))
    im_merge.paste(im_part2, (im_part1.width, 0))
    return im_merge

def merge_large_brown_couch(im_object):
    im_merge = Image.new("RGBA", (im_object.width, im_object.height), (0, 0, 0, 0))
    im1 = im_object.crop((0, 0, im_object.width * (2 / 5), im_object.height / 2))
    im2 = im_object.crop((im1.width, 0, im_object.width * (3 / 5) , im_object.height))
    im3 = im_object.crop((im1.width + im2.width, 0, im_object.width, im_object.height / 2))
    im_merge.paste(im1, (0, 0))
    im_merge.paste(im2, (im1.width, 0))
    im_merge.paste(im3, (im1.width + im2.width, 0))
    return im_merge

def convert_furniture(
    change,
    mod_folder_path,
    config_schema_options,
    dynamic_tokens,
    keywords,
    objects_replaced,
):

    file = change["FromFile"]
    target_file = Path(change["Target"].lower()).with_suffix(".png")

    found_placeholders = re.findall(r"{{(.*?)}}", file)
    file_season = False

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
        file,
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
            height = furniture_coords_info[(tilesheet_X, tilesheet_Y)]["Height"]
            object_name = furniture_coords_info[tilesheet_X, tilesheet_Y]["Object"]
            print(f"Object replacement known: {object_name}")
            object_list = [object_name]
            if tilesheet_coords["Width"] != width or tilesheet_coords["Height"] != height:
                print("Consecutive objects in X-direction replaced, splitting...")
                object_list = split_replacement(
                    tilesheet_coords, "Width"
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
        if "object_list" in locals():
            for object_name in object_list:
                data = furniture_objects_info[object_name]
                object_type = data["Type"]
                new_file_path = get_file_path(
                    file, object_name, mod_folder_path, file_season
                )
                if "FromArea" in change:
                    if len(object_list) == 1:
                        X = change["FromArea"]["X"]
                        Y = change["FromArea"]["Y"]
                        object_width = change["FromArea"]["Width"]
                        object_height = change["FromArea"]["Height"]
                        X_right = X + object_width
                        Y_bottom = Y + object_height
                        im_object = im.crop((X, Y, X_right, Y_bottom))
                    else:
                        X = data["X"]
                        Y = data["Y"]
                        object_width = data["Width"]
                        object_height = data["Height"]
                        X_right = X + object_width
                        Y_bottom = Y + object_height
                        im_object = im.crop((X, Y, X_right, Y_bottom))
                    if object_type == "rug":
                        im_object = merge_rug_sprites(im_object)
                    elif object_name == "Large Brown Couch":
                        im_object = merge_large_brown_couch(im_object)
                    print(f"Cropped {object_name} from {Path(file)}.")
                else:
                    im_object = im
                    object_width, object_height = im_object.size
                im_object.save(new_file_path)
                image_variations.append(im_object)
                objects_replaced[object_name] = image_variations

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

                furniture_Front_path = Path(re.sub("furniture", "furnitureFront", file))
                furniture_Front_path = mod_folder_path / furniture_Front_path
                if furniture_Front_path.exists():
                    im_front = Image.open(furniture_Front_path)
                    front_X = data["X"]
                    front_Y = data["Y"]
                    front_object_width = data["Width"]
                    front_object_height = data["Height"]
                    front_X_right = front_X + front_object_width
                    front_Y_bottom = front_Y + front_object_height
                    im_object_front = im_front.crop((front_X, front_Y, front_X_right, front_Y_bottom))
                    # * check for random transparent pixels
                    num_colors = im_object_front.size[0] * im_object_front.size[1]
                    front_colors = sorted(x for x in im_object_front.getcolors(num_colors))
                    front_transparencies = [x[3] for _, x in front_colors]
                    # * front image has no solid pixels
                    if all(x != 255 for x in front_transparencies):
                        continue
                    print("Letting sit...")
                    im_front_merge = Image.new("RGBA", (im_object.width, im_object.height * 2))
                    im_front_merge.paste(im_object, (0, 0), im_object)
                    im_front_merge.paste(im_object_front, (0, im_object.height), im_object_front)
                    im_front_merge.save(new_file_path)

                    with open(texture_json_path, "r", encoding="utf-8") as json_file:
                        texture_json = json5.loads(json_file.read())
                    texture_json["TextureHeight"] = im_front_merge.height
                    with open(texture_json_path, "w", encoding="utf-8") as json_file:
                        json.dump(texture_json, json_file, indent=4)

        else:
            print("Trying to identify...")
            for coords, values in furniture_coords_info.items():
                object_name = values["Object"]
                object_width = values["Width"]
                object_height = values["Height"]

                X, Y = [*coords]
                X_right = X + object_width
                Y_bottom = Y + object_height

                im_vanilla = Image.open(target_file).convert("RGBA")
                background = Image.new("RGBA", im_vanilla.size,  (0, 0, 0, 0))
                background.paste(im_vanilla, (0, 0), im_vanilla)
                im_vanilla = background
                im_cropped_vanilla = im_vanilla.crop((X, Y, X_right, Y_bottom))

                im_mod = Image.open(mod_folder_path / file).convert("RGBA")
                background = Image.new("RGBA", im_mod.size, (0, 0, 0, 0))
                background.paste(im_mod, (0, 0), im_mod)
                im_mod = background
                im_cropped_mod = im_mod.crop((X, Y, X_right, Y_bottom))

                if values["Type"] == "rug" and values["Rotations"] != "1":
                    im_cropped_vanilla = merge_rug_sprites(im_cropped_vanilla)
                    im_cropped_mod = merge_rug_sprites(im_cropped_mod)
                elif object_name == "Large Brown Couch":
                    im_cropped_vanilla = merge_large_brown_couch(im_cropped_vanilla)
                    im_cropped_mod = merge_large_brown_couch(im_cropped_mod)

                diff = ImageChops.difference(im_cropped_vanilla, im_cropped_mod)
                if diff.getbbox() is None and np.sum(np.array(diff.getdata())) < 5000: # got a hit
                    continue
                num_colors = im_cropped_mod.size[0] * im_cropped_mod.size[1]
                if sorted(im_cropped_vanilla.getcolors(num_colors)) != sorted(im_cropped_mod.getcolors(num_colors)):
                    # make sure it's not just random transparent pixels
                    mod_colors = sorted(x for x in im_cropped_mod.getcolors(num_colors))
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
                    # im_vanilla = Image.open(target_file)
                    # im_mod = Image.open(mod_folder_path / file)
                    # im_cropped_vanilla = im_vanilla.crop((X, Y, X_right, Y_bottom))
                    # im_cropped_mod = im_mod.crop((X, Y, X_right, Y_bottom))
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
                        "Furniture",
                        int(object_width),
                        int(object_height),
                        keywords,
                        file_season,
                    )

                    furniture_Front_path = Path(re.sub("furniture", "furnitureFront", file))
                    furniture_Front_path = mod_folder_path / furniture_Front_path
                    if furniture_Front_path.exists():
                        im_front = Image.open(furniture_Front_path)
                        data = furniture_objects_info[object_name]
                        front_X = data["X"]
                        front_Y = data["Y"]
                        front_object_width = data["Width"]
                        front_object_height = data["Height"]
                        front_X_right = front_X + front_object_width
                        front_Y_bottom = front_Y + front_object_height
                        im_object_front = im_front.crop((front_X, front_Y, front_X_right, front_Y_bottom))
                        # * check for random transparent pixels
                        num_colors = im_object_front.size[0] * im_object_front.size[1]
                        front_colors = sorted(x for x in im_object_front.getcolors(num_colors))
                        front_transparencies = [x[3] for _, x in front_colors]
                        # * front image has no solid pixels
                        if all(x != 255 for x in front_transparencies):
                            continue
                        print(f"Let sit on {object_name}...\n")
                        im_front_merge = Image.new("RGBA", (im_cropped_mod.width, im_cropped_mod.height * 2))
                        im_front_merge.paste(im_cropped_mod, (0, 0), im_cropped_mod)
                        im_front_merge.paste(im_object_front, (0, im_cropped_mod.height), im_object_front)
                        im_front_merge.save(new_file_path)

                        with open(texture_json_path, "r", encoding="utf-8") as json_file:
                            texture_json = json5.loads(json_file.read())
                        texture_json["TextureHeight"] = im_front_merge.height
                        with open(texture_json_path, "w", encoding="utf-8") as json_file:
                            json.dump(texture_json, json_file, indent=4)

    return objects_replaced
