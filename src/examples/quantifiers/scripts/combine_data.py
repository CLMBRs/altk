import pandas as pd

from yaml import load
from ultk.effcomm.tradeoff import pareto_min_distances

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
    keys = ["name", "comm_cost", "complexity", "type", "naturalness"]
    dominating_languages = yaml_to_dataframe(
        "quantifiers/outputs/dominating_languages.yml", keys
    )
    explored_languages = yaml_to_dataframe(
        "quantifiers/outputs/explored_languages.yml", keys
    )
    all_data = pd.concat([explored_languages, dominating_languages], ignore_index=True)

    # Measure optimality
    all_data["optimality"] = 1 - pareto_min_distances(
        all_data[["comm_cost", "complexity"]].values,
        all_data[all_data.type == "dominant"][["comm_cost", "complexity"]].values,
    )

    all_data.to_csv("quantifiers/outputs/combined_data.csv", index=False)
