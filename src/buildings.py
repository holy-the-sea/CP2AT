# ! /usr/bin/python
import re
import os
from pathlib import Path
from collections import defaultdict

from PIL import Image

from src.file_names import expand_target_variations, get_file_path, get_file_variations
from src.generate_jsons import generate_texture_json


def convert_buildings(
    change,
    mod_folder_path,
    config_schema_options,
    dynamic_tokens,
    keywords,
    objects_replaced,
):
    file = change["FromFile"]
    target = change["Target"]
    building = Path(target).stem
    print(f"Converting {building}...")

    found_placeholders = re.findall(r"{{(.*?)}}", file)
    found_seasons = False
    file_season = False

    image_variations = []
    house_image_variations = defaultdict(list)

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
        file,
        mod_folder_path,
        config_schema_options,
        dynamic_tokens,
    )

    # * check for whole tilesheet replacement
    if "FromArea" in change:
        X = change["FromArea"]["X"]
        Y = change["FromArea"]["Y"]
        width = change["FromArea"]["Width"]
        height = change["FromArea"]["Height"]
        X_right = X + width
        Y_bottom = Y + height
    else:
        # TODO: fix this escape
        X, Y = False, False
        

    for file in file_variations:
        if re.search("{{.*?}}", file):
            continue
        im = Image.open(mod_folder_path / file)
        if "FromArea" not in change:
            width, height = im.size

        # * check if seasonal variations
        if found_seasons or any(
            x in file for x in ["spring", "summer", "fall", "winter"]
        ):
            file_season = (
                re.search(r"(spring|summer|fall|winter)", file).group(1).capitalize()
            )
        else:
            file_season = False

        new_file_path = get_file_path(file, building, mod_folder_path, file_season)

        # farmhouses need to be split into different upgrades for Alternative Textures
        if target.lower() == "buildings/houses":
            house_height = 144
            if X is False:
                for i in range(3):
                    house_Y = Y + house_height * i
                    house_Y_bottom = house_height * (i + 1)
                    X = 0
                    X_right = 160
                    im_house = Image.new("RGBA", (160, 144))
                    im_cropped_house = im.crop((X, house_Y, X_right, house_Y_bottom))
                    im_house.paste(im_cropped_house, (0, 0), im_cropped_house)
                    farmhouse_folder = Path(new_file_path).parent / f"Farmhouse_{i}"
                    if not farmhouse_folder.exists():
                        os.mkdir(farmhouse_folder)
                    for _, _, files in os.walk(farmhouse_folder):
                        texture_num = len(
                            [
                                file
                                for file in files
                                if re.match(r"texture_\d+.png", file)
                            ]
                        )
                        break
                    im_house.save(
                        farmhouse_folder / f"texture_{texture_num}.png"
                    )  # ! save
                    house_image_variations[f"house_{i}"].append(im_house)
                    texture_json_path = farmhouse_folder / "texture.json"
                    generate_texture_json(
                        texture_json_path,
                        building,
                        "Building",
                        320,
                        144,
                        keywords,
                        file_season,
                    )
        # TODO: add PaintMasks

        else:
            if X:
                im = im.crop((X, Y, X_right, Y_bottom))
                im.save(new_file_path)  # ! save
                image_variations.append(im)
            else:
                im.save(new_file_path)  # ! save
                image_variations.append(im)
            texture_json_path = Path(new_file_path).parent / "texture.json"
            generate_texture_json(
                texture_json_path,
                building,
                "Building",
                width,
                height,
                keywords,
                file_season,
            )
    if target.lower() == "buildings/houses":
        objects_replaced.update(house_image_variations)
        print(f"Done converting {building}.\n")
        return objects_replaced
    objects_replaced[building] = image_variations
    print(f"Done converting {building}.\n")
    return objects_replaced
