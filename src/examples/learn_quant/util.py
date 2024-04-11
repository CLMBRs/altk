from typing import Callable, Any
import pandas as pd

from yaml import load, dump
from typing import Iterable, Union
import pickle

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ultk.language.grammar import GrammaticalExpression
from ultk.language.language import Expression, Language
from ultk.language.semantics import Meaning, Universe

from learn_quant.grammar import quantifiers_grammar
from learn_quant.meaning import create_universe

def read_expressions(
    filename: str, universe: Universe = None, return_by_meaning=True
) -> tuple[list[GrammaticalExpression], dict[Meaning, Expression]]:
    """Read expressions from a YAML file.
    Assumes that the file is a list, and that each item in the list has a field
    "grammatical_expression" with an expression that can be parsed by the
    indefinites_grammar.
    """
    quantifiers_grammar.add_indices_as_primitives(universe.x_size)

    with open(filename, "r") as f:
        expression_list = load(f, Loader=Loader)
    parsed_exprs = [
        quantifiers_grammar.parse(expr_dict["grammatical_expression"])
        for expr_dict in expression_list
    ]
    if universe is not None:
        [expr.evaluate(universe) for expr in parsed_exprs]
    by_meaning = {}
    if return_by_meaning:
        by_meaning = {expr.meaning: expr for expr in parsed_exprs}
    return parsed_exprs, by_meaning

def filter_expressions_by_rules(rules: list, expressions):
    return list(filter(lambda x: str(x) in rules, expressions))


import os

def read_expressions_from_folder(folder: str, return_by_meaning=True) -> tuple[list[GrammaticalExpression], dict[Meaning, Expression]]:
    """Read expressions from a YAML file in a specified folder.
    Assumes that the file is a list, and that each item in the list has a field
    "grammatical_expression" with an expression that can be parsed by the
    indefinites_grammar. Assumes there is a master universe pkl file in the
    """
    expressions_file = os.path.join(folder, 'generated_expressions.yml')  # replace 'filename.yaml' with your actual filename
    universe_file = os.path.join(folder, 'master_universe.pkl')  # replace 'universe.pkl' with your actual universe filename

    with open(universe_file, 'rb') as f:
        universe = pickle.load(f)

    quantifiers_grammar.add_indices_as_primitives(universe.x_size)

    with open(expressions_file, "r") as f:
        expression_list = load(f, Loader=Loader)
    parsed_exprs = [
        quantifiers_grammar.parse(expr_dict["grammatical_expression"])
        for expr_dict in expression_list
    ]
    if universe is not None:
        [expr.evaluate(universe) for expr in parsed_exprs]
    by_meaning = {}
    if return_by_meaning:
        by_meaning = {expr.meaning: expr for expr in parsed_exprs}
    return parsed_exprs, by_meaning, universe