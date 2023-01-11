import json
# from math import floor
from pathlib import Path

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
    with open(furniture_objects_path) as json_file:
        furniture_objects_data = json5.loads(json_file.read())
    furniture_objects_data = {key: value.split('/') for key, value in furniture_objects_data.items()}

    furniture_objects_dict = {}
    
    for tileIndex, data in furniture_objects_data.items():

        X = int(tileIndex) * 16 % 512
        Y = int(tileIndex) * 16 // 512 * 16
        
        if data[2] == "-1":
            width, height = furniture_defaults[data[1]]["Width"], furniture_defaults[data[1]]["Height"]
        else:
            width, height = data[2].split(' ')
            width = int(width) * 16
            height = int(height) * 16
        
        if data[4] != "1":
            if "chair" in data[1]:
                rot_width = width * 3
                rot_height = height
            elif data[1] == "bench" or data[1] == "couch":
                rot_width = 80
                rot_height = 48
            elif data[1] == "dresser":
                rot_width = 48
                rot_height = 48
            elif data[1] == "long table":
                rot_width = 112
                rot_height = 76
            elif "End Table" in data[0]:
                rot_width = 32
                rot_height = 32
            elif data[1] == "rug":
                continue
            #     rot_width = 48
            #     rot_height = 48
            # elif data[1] == "rug":
            #     rot_width = width * 1.5
            #     rot_height = width
                
            furniture_objects_dict[data[0]] = {"X": X, "Y": Y, "Type": data[1], "Width": rot_width, "Height": rot_height}
                
        else:
            furniture_objects_dict[data[0]] = {"X": X, "Y": Y, "Type": data[1], "Width": width, "Height": height}
        

    with open("furniture_coords.json", "w") as file:
        json.dump(furniture_objects_dict, file, indent=4)
    return furniture_objects_dict

furniture_objects_info = _get_furniture_coords()