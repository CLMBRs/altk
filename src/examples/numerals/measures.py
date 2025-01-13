from ultk.language.grammar import GrammaticalExpression
from ultk.language.language import Language, aggregate_expression_complexity
from ultk.language.semantics import Meaning

from .meaning import universe as numerals_universe
from .numerals_language import NumeralsLanguage, get_singleton_meaning

prior = numerals_universe.prior_numpy

def weighted_complexity(expr: GrammaticalExpression) -> float:
    """P(n) * ms_complexity(n, L)"""
    return prior[get_singleton_meaning(expr)-1] * len(expr)

def avg_morph_complexity(language: NumeralsLanguage) -> float:
    return aggregate_expression_complexity(
        language, weighted_complexity,
    )

def lexicon_size(language: NumeralsLanguage) -> float:
    return len(language)