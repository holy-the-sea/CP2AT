from pathlib import Path
import re

from PIL import Image

from src.file_names import expand_target_variations, get_file_path, get_file_variations
from src.generate_jsons import generate_texture_json

def convert_animals(
    change,
    mod_folder_path,
    config_schema_options,
    dynamic_tokens,
    keywords,
    objects_replaced
):
    file = change["FromFile"]
    target = change["Target"]
    animal = Path(target).stem
    if animal.lower() in ["babybrown cow", "babygoat", "babyostrich", "babypig", "babysheep", "babywhite cow", "brown cow", "goat", "ostrich", "pig", "shearedsheep", "sheep", "white cow"]:
        width = 128
        height = 160
    elif animal.lower() in ["babygolden chicken", "babywhite chicken", "duck"]:
        width = 64
        height = 224
    elif "cat" in animal.lower():
        width = 128
        height = 256
    elif "dog" in animal.lower():
        width = 128
        height = 288
    elif animal.lower() == "horse":
        width = 224
        height = 128
    else:
        width = 64
        height = 112
    print(f"Converting {animal}...")

    found_placeholders = re.findall(r"{{(.*?)}}", file)
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
            dynamic_tokens
        )
    file_variations = expand_target_variations(
        file_variations,
        file,
        mod_folder_path,
        config_schema_options,
        dynamic_tokens
    )

    for file in file_variations:
        if re.search("{{.*?}}", file):
            continue
        im = Image.open(mod_folder_path / file)
        new_file_path = get_file_path(
            file, animal, mod_folder_path, False
        )
        im.save(new_file_path)
        image_variations.append(im)
        objects_replaced[animal] = image_variations
        texture_json_path = Path(new_file_path).parent / "texture.json"
        generate_texture_json(
            texture_json_path,
            animal,
            "Character",
            width,
            height,
            keywords,
            False
        )
    print("Done.")
    return objects_replaced