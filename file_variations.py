#! /usr/bin/python

import re
from itertools import product

def get_file_variations(file, mod_folder_path, placeholder_tokens, *args):
    placeholder_options = {}
    for arg in args: # combine ConfigSchema and DynamicTokens (probably)
        placeholder_options.update(arg)

    seasons = ["spring", "summer", "fall", "winter"]
    found_season = False

    file_variations = []
    cartesian = []

    for placeholder in placeholder_tokens:

        try: # found in either ConfigSchema or DynamicTokens
            token = placeholder_options[placeholder]
            cartesian.append(token)
            continue
        except KeyError:
            pass

        if placeholder.lower() == "season":
            cartesian.append(seasons)
            found_season = True
        elif "|contains=" in placeholder:
            cartesian.append(["true", "false"])

    for cartesian_product in product(*cartesian):
        file_variant = file
        for i, placeholder in enumerate(cartesian_product):
            file_variant = re.sub(r"{{.*?}}", cartesian_product[i], file_variant, count=1)
            if (mod_folder_path / file_variant).exists():
                file_variations.append(file_variant)
            elif "{{Target}}" in file_variant:
                file_variations.append(file_variant)

    return file_variations, found_season