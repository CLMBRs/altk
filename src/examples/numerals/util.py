from typing import Callable, Any
import pandas as pd

from yaml import dump, Dumper

from ultk.language.language import Expression, Language
from ultk.language.semantics import Meaning
from ultk.util.frozendict import FrozenDict

from .meaning import universe as numerals_universe


def read_natural_languages(filename: str) -> set[Language]:
    """Read the natural languages from a CSV file.
    Assumes that each row is one expression, with unique strings in "language" column identifying
    which expressions belong to which languages.
    Assumes that there is a boolean-valued column for each Referent in the numerals_universe,
    identified by its name.

    Args:
        filename: the file to read

    Returns:
        a list of Languages
    """
    lang_data = pd.read_csv(filename)
    lang_data["flavors"] = lang_data.apply(
        lambda row: row[row == True].index.tolist(), axis=1
    )
    # group data frame by language
    language_frame = lang_data.groupby("language")
    languages = set()
    # iterate through each language
    for lang, items in language_frame:
        cur_expressions = []
        for item in items.itertuples():
            # generate Meaning from list of flavors
            cur_meaning = Meaning(
                FrozenDict(
                    {
                        referent: referent.name in item.flavors
                        for referent in numerals_universe
                    }
                ),
                numerals_universe,
            )
            # add Expression with form and Meaning
            cur_expressions.append(Expression(item.expression, cur_meaning))
        # add Language with its Expressions
        languages.add(Language(tuple(cur_expressions), name=lang, natural=True))
    return languages


def write_languages(
    languages: list[Language],
    filename: str,
    properties_to_add: dict[str, Callable[[int, Language], Any]] = {},
) -> None:
    lang_dicts = [
        language.as_dict_with_properties(
            **{key: properties_to_add[key](idx, language) for key in properties_to_add}
        )
        for idx, language in enumerate(languages)
    ]
    with open(filename, "w+") as f:
        dump(lang_dicts, f, Dumper=Dumper)


def extract_integers(file_path):
    integers = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.isdigit():
                integers.append(int(line))
    return integers