import requests
import yaml
import pandas as pd
from tqdm import tqdm
from typing import Any

from ultk.language.semantics import FrozenDict, Universe
from ultk.language.language import Expression, Meaning, Language
from .meaning import universe as modals_universe

ALLOWED_REFERENCE_TYPES = ["paper-journal", "elicitation"]
REFERENCE_GRAMMAR = "reference-grammar"
REFERENCE_TYPES = [REFERENCE_GRAMMAR] + ALLOWED_REFERENCE_TYPES
REFERENCE_TYPE_KEY = "Reference-type"
LANGUAGE_IS_COMPLETE_KEY = "Complete-language"
FAMILY_KEY = "Family"

METADATA_FN = "metadata.yml"
MODALS_FN = "modals.csv"

API_URL = "https://api.github.com/repos/nathimel/modals-effcomm/contents/data/natural_languages?ref=main"



def load_natural_languages(universe: Universe = modals_universe) -> list[Language]:
    return dataframes_to_languages(get_modals_data(), universe)


def get_modals_data() -> dict[pd.DataFrame]:
    # Make the request
    response = requests.get(API_URL)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch folder contents: {response.status_code}\n{response.text}"
        )

    # Parse the response JSON
    contents = response.json()

    # Filter for subfolders (type == 'dir')
    subfolders = [item["name"] for item in contents if item["type"] == "dir"]
    base_raw_link = f"https://raw.githubusercontent.com/nathimel/modals-effcomm/refs/heads/main/data/natural_languages"

    path_map = {
        subfolder: {
            "modals": f"{base_raw_link}/{subfolder}/modals.csv",
            "metadata": f"{base_raw_link}/{subfolder}/metadata.yml",
        }
        for subfolder in subfolders
    }

    dataframes = load_csvs(path_map)
    return dataframes


def load_csvs(language_dirs: dict[str, dict[str, str]]) -> dict[str, pd.DataFrame]:
    dataframes = dict()
    print(f"Loading modals data from {API_URL}")
    for lang in tqdm(language_dirs):
        # Ensure that is one of allowed reference types
        metadata_path = language_dirs[lang]["metadata"]
        response = requests.get(metadata_path)

        # Parse the YAML content as dict
        try:
            metadata = yaml.safe_load(response.text)
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing YAML: {e}")

        reference_type = metadata[REFERENCE_TYPE_KEY]
        # must be paper-journal or elicitation
        if reference_type in ALLOWED_REFERENCE_TYPES:
            modals_fn = language_dirs[lang]["modals"]
            if FAMILY_KEY not in metadata:
                pass
            dataframes[lang] = pd.read_csv(modals_fn)
        else:
            # Skip reference-grammar obtained data if incomplete.
            print(f"Data for {lang} is of type {reference_type}; skipping.")

    return dataframes


def process_can_express(val: Any, can_express: dict = {True: [1], False: ["?", 0]}):
    """For an observation of whether a modal can_express a force-flavor pair, interpret ? as 1.

    Note that the existence of ? in the csv confuses pandas, and causes the type of can_express to be str.

    Args:
        val: the value of the can_express column, possibly an int or str

    Returns:
        boolean representing 'yes' if the value should be interpreted as True, False otherwise
    """
    if isinstance(val, int):
        return val
    if val.isnumeric():
        return bool(int(val))

    # different results depending on interpretation of '?'
    if val in can_express[True]:
        return True
    return False


def dataframes_to_languages(
    dataframes: dict[str, pd.DataFrame], universe: Universe
) -> list[Language]:
    """Convert a list of dataframes to a list of ultk Languages."""
    languages: list[Language] = []
    for language_name, df in dataframes.items():
        print(f"Adding {language_name}")
        lang = dataframe_to_language(df, language_name, universe)
        if lang is not None:
            languages.append(lang)
    return languages


def dataframe_to_language(
    df: pd.DataFrame,
    language_name: str,
    universe: Universe,
) -> Language:
    """Construct a ultk Language from a dataframe of (expression, meaning) observations by iterating over each row and indicating whether the expression can express the meaning."""
    forces = set(ref.force for ref in universe)
    flavors = set(ref.flavor for ref in universe)

    vocabulary = {}

    # only look at positive polarity modals
    if "polarity" in df:
        df_positive = df[df["polarity"] == "positive"]
    else:
        df_positive = df

    # add each observation
    for _, row in df_positive.iterrows():
        modal = row["expression"]
        # initialize an expression's set of meanings
        if modal not in vocabulary:
            vocabulary[modal] = set()

        # Add only the flavors specified as possible for the experiment
        if row["flavor"] in flavors and row["force"] in forces:
            if process_can_express(row["can_express"]):
                observation = f"{row['force']}+{row['flavor']}"
                vocabulary[modal].add(observation)

    # Convert vocabulary into list of Expressions
    experiment_vocabulary = []
    for modal in vocabulary:
        form = modal
        meaning = Meaning(
            mapping=FrozenDict(
                {referent: referent.name in vocabulary[modal] for referent in universe}
            ),
            universe=universe,
        )

        if (
            meaning.is_uniformly_false()
        ):  # often there will be no usable referents due to can_express being False, above
            continue
        # search for a matching recorded meaning
        experiment_vocabulary.append(
            Expression(
                form,
                meaning,
            )
        )

    if experiment_vocabulary:
        return Language(
            expressions=experiment_vocabulary, name=language_name, natural=True
        )
    return
