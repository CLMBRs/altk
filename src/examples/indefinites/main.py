from typing import Iterable, Generator
import pandas as pd
from altk.language.language import Expression
from altk.language.semantics import Universe, Meaning, all_meanings

from grammar import indefinites_grammar
from meaning import universe as indefinites_universe


def all_expressions(meanings: Iterable[Meaning]) -> Generator[Expression, None, None]:
    for idx, meaning in enumerate(meanings):
        yield Expression(f"expr-{idx}", meaning)


if __name__ == "__main__":

    print(indefinites_universe)

    """
    for exp in indefinites_grammar.enumerate(3):
        print(exp)
        print(exp.to_meaning(indefinites_universe))
    """

    expressions = all_expressions(all_meanings(indefinites_universe))
    for exp in expressions:
        print(exp)