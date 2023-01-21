# ! /usr/bin/python

import re
from collections import defaultdict
from pathlib import Path

from PIL import Image
from src.file_names import get_file_path, get_file_variations, expand_target_variations
from src.generate_jsons import generate_texture_json


def convert_trees(
    change,
    mod_folder_path,
    config_schema_options,
    dynamic_tokens,
    keywords,
    objects_replaced,
):
    file = change["FromFile"]
    target_file = change["Target"]

    found_placeholders = re.findall(r"{{(.*?)}}", str(file))
    found_seasons = False
    file_season = False

    image_variations = []

    fruit_trees = [
        "Cherry",
        "Apricot",
        "Orange",
        "Peach",
        "Pomegranate",
        "Apple",
        "Banana",
        "Mango",
    ]
    fruit_tree_variations = defaultdict(list)

    nonfruit_trees = ["Oak", "Maple", "Pine"]
    nonfruit_tree_variations = defaultdict(list)

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
    print(file_variations)

    try:
        X = change["FromArea"]["X"]
        Y = change["FromArea"]["Y"]
        width = change["FromArea"]["Width"]
        height = change["FromArea"]["Height"]
        X_right = X + width
        Y_bottom = Y + height
    except KeyError:
        X, Y, width, height = False, False, False, False
        # ! fix this escape

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

        if "fruittrees" in target_file.lower():
            X = 0
            X_right = im.size[0]
            tree_height = 80
            for i, fruit in enumerate(fruit_trees):
                print(f"Converting {fruit} Sapling... from {Path(file)}")
                new_file_path = get_file_path(
                    file, fruit.capitalize(), mod_folder_path, file_season
                )

                if "ToArea" not in change.keys():
                    tree_Y = Y + tree_height * i
                    tree_Y_bottom = tree_height * (i + 1)
                    im_fruit_tree = im.crop((X, tree_Y, X_right, tree_Y_bottom))
                im_fruit_tree.save(new_file_path)
                fruit_tree_variations[fruit].append(im_fruit_tree)
                texture_json_path = Path(new_file_path).parent / "texture.json"
                generate_texture_json(
                    texture_json_path,
                    fruit + " Sapling",
                    "FruitTree",
                    432,
                    80,
                    keywords,
                    file_season,
                )
            objects_replaced.update(fruit_tree_variations)
            # print(f"Done converting Fruit Trees from {file}.\n")
            continue

        try:
            tree_num = re.search(r"tree(\d)", str(target_file)).group(1)
            if tree_num == "8":
                tree_type = "Mahogany"
            else:
                tree_type = nonfruit_trees[int(tree_num) - 1]
        except AttributeError:
            pass
        try:
            tree_type = (
                re.search(r"tree_(palm\d?)", str(target_file)).group(1).capitalize()
            )
        except AttributeError:
            pass
        try:
            tree_type = (
                re.search(r"(mushroom)_tree", str(target_file)).group(1).capitalize()
            )
        except AttributeError:
            pass
        print(f"Converting {tree_type} Sapling from {Path(file)}...")
        new_file_path = get_file_path(
            file, tree_type.capitalize(), mod_folder_path, file_season
        )
        if X:
            im = im.crop((X, Y, X_right, Y_bottom))
            im.save(new_file_path)
            image_variations.append(im)
        else:
            im.save(new_file_path)  # ! save
            image_variations.append(im)
        texture_json_path = Path(new_file_path).parent / "texture.json"
        generate_texture_json(
            texture_json_path,
            tree_type + " Sapling",
            "Tree",
            48,
            160,
            keywords,
            file_season,
        )

    if "fruittrees" in str(target_file).lower():
        objects_replaced.update(fruit_tree_variations)
        print("Done converting Fruit Trees.\n")
        return objects_replaced

    objects_replaced[tree_type] = nonfruit_tree_variations
    print(f"Done converting {tree_type.capitalize()} Tree from {Path(file).parent}\n")
    return objects_replaced
