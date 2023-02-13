#! /usr/bin/python

import json
from pathlib import Path
import numpy as np

import json5


def _get_springobjects_coords():

    spring_objects_path = Path("Data/ObjectInformation.json")
    with open(spring_objects_path, encoding="utf-8") as json_file:
        spring_objects_json = json5.loads(json_file.read())

    x_list = np.arange(0, 384, 16)
    y_list = np.arange(0, 624, 16)

    tile_num = len(y_list)
    repeat_num = len(x_list)

    x_list = np.tile(x_list, tile_num)
    y_list = np.repeat(y_list, repeat_num)

    spring_objects_coords = np.stack([x_list, y_list], axis=1)

    multiple_instances = []
    names = [value.split("/")[0] for value in spring_objects_json.values()]
    for object_name in np.unique(names):
        num_object = sum(object_name == name for name in names)
        if num_object > 1:
            multiple_instances.append(object_name)

    standard_width = 16
    standard_height = 16

    spring_objects_dict = {}

    for key, value in spring_objects_json.items():
        object_name = value.split("/")[0]
        key = int(key)

        x_left = int(spring_objects_coords[key][0])
        y_top = int(spring_objects_coords[key][1])

        if object_name in multiple_instances:
            id_num = sum(object_name in object_key for object_key in spring_objects_dict)
            id_name = f"{object_name}_{id_num}"
        else:
            id_name = object_name
        spring_objects_dict[id_name] = {
            "X": x_left,
            "Y": y_top,
            "Width": standard_width,
            "Height": standard_height
        }
    with open("src/coords_info/springobjects_coords.json", "w", encoding="utf-8") as json_file:
        json.dump(spring_objects_dict, json_file, indent=4, sort_keys=False)

    return spring_objects_dict

spring_objects_info = _get_springobjects_coords()
