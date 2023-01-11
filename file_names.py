#! /usr/bin/python

import os
import re
from pathlib import Path


def get_file_path(file, object_name, mod_folder_path, file_season):
    object_name = re.sub(r"_\d+", "", object_name)
    new_folder_path = (mod_folder_path / file).parent
    if file_season is not False:
        new_folder_path = new_folder_path / file_season
    else:
        new_folder_path = new_folder_path / "ALL"
    new_folder_path = new_folder_path / object_name

    new_folder_path = re.sub(r"assets", "Textures", str(new_folder_path), flags=re.IGNORECASE)
    new_folder_path = Path(new_folder_path)
    if not new_folder_path.exists():
        new_folder_path.mkdir(parents=True, exist_ok=True)
    for _, _, files in os.walk(new_folder_path):
        texture_num = len([file for file in files if re.match(r"texture_\d+.png", file)])
        break
    new_file_path = new_folder_path / f"texture_{texture_num}.png"
    return str(new_file_path)