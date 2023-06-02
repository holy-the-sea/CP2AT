from pathlib import Path
import re

from PIL import Image

from src.file_names import expand_target_variations, get_file_path, get_file_variations
from src.generate_jsons import generate_texture_json

fence_types = {
    "Fence1": "Wood Fence",
    "Fence2": "Stone Fence",
    "Fence3": "Iron Fence",
    "Fence5": "Hardwood Fence"
}

def convert_fences(
    change,
    mod_folder_path,
    config_schema_options,
    dynamic_tokens,
    keywords,
    objects_replaced
):

    file = change["FromFile"]
    target_file = Path(change["Target"]).with_suffix(".png")
    fence = fence_types[target_file.stem]
    print(f"Converting {fence}...")

    found_placeholders = re.findall(r"{{(.*?)}}", file)
    found_seasons = False
    file_season = False

    image_variations = []

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
        dynamic_tokens
    )

    for file in file_variations:
        if re.search("{{.*?}}", file):
            continue
        im = Image.open(mod_folder_path / file)

        # * check if seasonal variations
        if found_seasons or any(
            x in file.lower() for x in ["spring", "summer", "fall", "winter"]
        ):
            file_season = (
                re.search(r"(spring|summer|fall|winter)", file).group(1).capitalize()
            )
        else:
            file_season = False

        im = Image.open(mod_folder_path / file)
        new_file_path = get_file_path(
            file, fence, mod_folder_path, file_season
        )
        im.save(new_file_path)
        image_variations.append(im)
        objects_replaced[fence] = image_variations
        texture_json_path = Path(new_file_path).parent / "texture.json"
        generate_texture_json(
            texture_json_path,
            fence,
            "Craftable",
            48,
            352,
            keywords,
            file_season
        )
    print("Done.")
    return objects_replaced