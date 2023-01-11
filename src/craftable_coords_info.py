#! /usr/bin/python

from pathlib import Path

import json
import json5
import numpy as np

# * python dictionary for craftable sprites and their coordinates
def _get_craftable_coordinate_info():

    craftable_objects_path = Path("Data/BigCraftablesInformation.json")

    with open(craftable_objects_path) as json_file:
        craftable_objects_json = json5.loads(json_file.read())

    x_list = np.arange(0, 128, 16)
    y_list = np.arange(0, 1152, 32)

    tile_num = len(y_list)
    repeat_num = len(x_list)

    x_list = np.tile(x_list, tile_num)
    y_list = np.repeat(y_list, repeat_num)

    craftable_coords = np.stack([x_list, y_list], axis=1)

    multiple_instances = []
    names = [value.split("/")[0] for value in craftable_objects_json.values()]
    for object in np.unique(names):
        num_object = sum([object == name for name in names])
        if num_object > 1:
            multiple_instances.append(object)

    standard_width = 16
    standard_height = 32

    craftable_objects_dict = {}

    for key, value in craftable_objects_json.items():
        object_name = value.split("/")[0]
        key = int(key)
        next_key = key + 1

        while str(next_key) not in craftable_objects_json:
            next_key += 1
            if next_key - key >= 8:
                break
        width = (next_key - key) * standard_width
        if (
            key == 90
            or key == 167
            or key == 175
            or key == 239
            or key == 265
            or key == 280
        ):
            width = 16
        elif key == 219:
            width = 32
        elif key == 256:
            width = 96

        x_left = int(craftable_coords[key][0])
        y_top = int(craftable_coords[key][1])

        if object_name in multiple_instances:
            id_num = sum(
                [object_name in object_key for object_key in craftable_objects_dict]
            )
            id_name = f"{object_name}_{id_num}"
            if id_name == "Campfire_0":
                id_name = "Campfire"
            craftable_objects_dict[id_name] = {
                "X": x_left,
                "Y": y_top,
                "Width": width,
                "Height": standard_height,
            }
        else:
            craftable_objects_dict[object_name] = {
                "X": x_left,
                "Y": y_top,
                "Width": width,
                "Height": standard_height,
            }

    craftable_objects_dict["Chest Color"] = {
        "X": 0,
        "Y": 672,
        "Width": 96,
        "Height": 64,
    }
    craftable_objects_dict["Chest Steel Fittings"] = {
        "X": 32,
        "Y": 512,
        "Width": 96,
        "Height": 32,
    }
    craftable_objects_dict["Chest Color Steel Fittings"] = {
        "X": 0,
        "Y": 704,
        "Width": 96,
        "Height": 32,
    }
    craftable_objects_dict["Stone Chest Steel Fittings"] = {
        "X": 0,
        "Y": 960,
        "Width": 96,
        "Height": 64,
    }

    with open("craftable_coords.json", "w") as file:
        json.dump(craftable_objects_dict, file, indent=4, sort_keys=True)

    return craftable_objects_dict

craftable_objects_info = _get_craftable_coordinate_info()
