#! /usr/bin/python

import json
from pathlib import Path
import numpy as np

import json5


def _get_furniture_coords():

    furniture_defaults = {
        "chair": {"Width": 16, "Height": 32},
        "bench": {"Width": 32, "Height": 32},
        "couch": {"Width": 48, "Height": 32},
        "armchair": {"Width": 32, "Height": 32},
        "dresser": {"Width": 32, "Height": 32},
        "long table": {"Width": 80, "Height": 48},
        "painting": {"Width": 32, "Height": 32},
        "lamp": {"Width": 16, "Height": 48},
        "decor": {"Width": 16, "Height": 32},
        "other": {"Width": 16, "Height": 32},
        "bookcase": {"Width": 32, "Height": 48},
        "table": {"Width": 32, "Height": 48},
        "rug": {"Width": 48, "Height": 32},
        "window": {"Width": 16, "Height": 32},
        "fireplace": {"Width": 32, "Height": 80},
        "bed": {"Width": 16, "Height": 32},
        "torch": {"Width": 16, "Height": 32},
        "sconce": {"Width": 16, "Height": 32},
    }

    furniture_objects_path = Path("Data/Furniture.json")
    with open(furniture_objects_path, encoding="utf-8") as json_file:
        furniture_objects_json = json5.loads(json_file.read())
    furniture_objects_data = {key: value.split("/") for key, value in furniture_objects_json.items()}

    multiple_instances = []
    names = [value.split("/")[0] for value in furniture_objects_json.values()]
    for object_name in np.unique(names):
        num_object = sum([object_name == name for name in names])
        if num_object > 1:
            multiple_instances.append(object_name)

    furniture_objects_dict = {}

    for tileIndex, data in furniture_objects_data.items():

        X = int(tileIndex) * 16 % 512
        Y = int(tileIndex) * 16 // 512 * 16

        if data[2] == "-1":
            width, height = (
                furniture_defaults[data[1]]["Width"],
                furniture_defaults[data[1]]["Height"],
            )
        else:
            width, height = data[2].split(" ")
            width = int(width) * 16
            height = int(height) * 16

        if data[4] != "1":
            if "chair" in data[1]:
                rot_width = width * 3
                rot_height = height
            elif data[1] == "bench":
                rot_width = width * 2.5
                rot_height = height * 1.5
            elif data[0] == "Large Brown Couch":
                rot_width = width * 2.5
                rot_height = height * 2
            elif data[1] == "couch":
                rot_width = width * (8 / 3)
                rot_height = height * 1.5
            elif data[1] == "dresser":
                rot_width = width * 2.5
                rot_height = height * 1.5
            elif "End Table" in data[0]:
                rot_width = width * 2
                rot_height = height
            elif data[1] == "table":
                rot_width = width * 1.5
                rot_height = height * 1.5
            elif data[1] == "long table":
                rot_width = width * (7 / 5)
                rot_height = height * (5 / 3)
            elif data[1] == "rug":
                if width < furniture_defaults["rug"]["Width"]:
                    rot_width = width * 1.5
                    rot_height = height * 2
                else:                    
                    rot_width = width * (5 / 3)
                    rot_height = height * 1.5

            furniture_objects_dict[data[0]] = {
                "X": X,
                "Y": Y,
                "Type": data[1],
                "Width": int(rot_width),
                "Height": int(rot_height),
                "Rotations": data[4]
            }
        # * beds don't rotate, but have made and unmade sprites
        if "bed" in data[1].lower():
            rot_width = width * 2
            rot_height = height
        else:
            rot_width = width
            rot_height = height
        if data[0] in multiple_instances:
            id_num = sum(
                [data[0] in object_key for object_key in furniture_objects_dict]
            )
            id_name = f"{data[0]}_{id_num}"
        else:
            id_name = data[0]
        furniture_objects_dict[id_name] = {
            "X": X,
            "Y": Y,
            "Type": data[1],
            "Width": int(rot_width),
            "Height": int(rot_height),
            "Rotations": data[4],
            "Default_Width": width,
            "Default_Height": height
        }
    with open("src/coords_info/furniture_coords.json", "w", encoding="utf-8") as file:
        json.dump(furniture_objects_dict, file, indent=4)
    return furniture_objects_dict


furniture_objects_info = _get_furniture_coords()
