from typing import Callable, Any
import pandas as pd

from yaml import load, dump
from typing import Iterable, Union


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


"""
def express_as_bool_vectors(
    expressions: list[GrammaticalExpression]
): -> Iterable[list[bool]]:
"""