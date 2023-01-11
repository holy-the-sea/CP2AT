#! /usr/bin/python
import re
from itertools import product


def get_config_schema(content_json):
    config_schema_options = {}
    if "ConfigSchema" in content_json.keys():
        config_schema_options = {
            key: re.split(r",\s+", value["AllowValues"])
            for (key, value) in content_json["ConfigSchema"].items()
        }
    return config_schema_options


def get_dynamic_tokens(content_json):
    dynamic_tokens = {}
    config_in_dynamic_tokens = []
    if "DynamicTokens" in content_json.keys():
        for token in content_json["DynamicTokens"]:
            token_name = token["Name"]
            token_value = token["Value"]

            try:
                token_when = token["When"]
            except KeyError:
                token_when = []
            if re.findall(r"{{.*?}}", token_value, flags=re.IGNORECASE):
                config_in_dynamic_tokens.append([token_name, token_value, token_when])
            if token_name not in dynamic_tokens:
                dynamic_tokens[token_name] = {token_value: token_when}
            else:
                dynamic_tokens[token_name].update({token_value: token_when})

    if config_in_dynamic_tokens:
        config_schema_options = get_config_schema(content_json)
        subbed_values = []

        for entry in config_in_dynamic_tokens:
            token_name, token_value, token_when = entry
            new_values = []

            token_text = re.findall(r"{{(.*?)}}", token_value)
            for text in token_text:

                try:  # look in ConfigSchema
                    config_values = config_schema_options[text]
                    new_values.append(config_values)
                    continue
                except KeyError:  # not found in ConfigSchema
                    pass

                try:  # look in DynamicTokens
                    dynamic_values = dynamic_tokens[text]
                except KeyError:
                    raise KeyError(
                        f"{text} not found in ConfigSchema or DynamicTokens, rest not implemented yet"
                    )
                try:  # check for when conditions when there are dynamic tokens
                    for when_key, when_value in token_when.items():
                        contain_values = re.search(
                            r"\|contains=(.*):?\s?", when_key, re.IGNORECASE
                        ).group(1)
                        contain_values = re.split(",\s+", contain_values, re.IGNORECASE)
                        if when_value:
                            dynamic_values = [
                                val for val in dynamic_values if val in contain_values
                            ]
                        elif when_value is False:
                            dynamic_values = [
                                val
                                for val in dynamic_values
                                if val not in contain_values
                            ]
                        new_values.append(dynamic_values)
                        continue
                except AttributeError:
                    continue
            for cartesian_product in product(*new_values):
                new_token_value = token_value
                for i, token in enumerate(cartesian_product):
                    new_token_value = re.sub(
                        r"{{.*?}}", cartesian_product[i], new_token_value, count=1
                    )
                subbed_values.append(new_token_value)
        for sub in subbed_values:
            if sub not in dynamic_tokens[token_name]:
                dynamic_tokens[token_name][sub] = {}

    return dynamic_tokens
