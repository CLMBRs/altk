import pandas as pd

from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def yaml_to_dataframe(filename: str, keys: list[str]) -> pd.DataFrame:
    with open(filename, "r") as f:
        language_dicts = load(f, Loader=Loader)
    return pd.DataFrame.from_records(
        [{key: lang_dict[key] for key in keys} for lang_dict in language_dicts]
    )


if __name__ == "__main__":
    keys = ["name", "comm_cost", "complexity", "type"]
    dominating_languages = yaml_to_dataframe(
        "numerals/outputs/dominating_languages.yml", keys
    )
    explored_languages = yaml_to_dataframe(
        "numerals/outputs/explored_languages.yml", keys
    )
    natural_languages = yaml_to_dataframe(
        "numerals/outputs/natural_languages.yml", keys
    )
    all_data = pd.concat(
        [explored_languages, dominating_languages, natural_languages], ignore_index=True
    )
    all_data.to_csv("numerals/outputs/combined_data.csv", index=False)
