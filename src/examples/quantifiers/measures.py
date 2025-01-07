
from ultk.effcomm.informativity import informativity, build_pairwise_matrix
from ultk.language.grammar import GrammaticalExpression
from ultk.language.language import Language, aggregate_expression_complexity
from ultk.language.semantics import Meaning

from .meaning import universe as quantifiers_universe, QuantifierModel


def complexity(
    language: Language, expressions_by_meaning: dict[Meaning, GrammaticalExpression]
) -> float:
    """Get complexity of a language via minimal expression length in LoT.

    Args:
        language: the Language to measure
        expressions_by_meaning: a dictionary with keys as `Meaning`s, that returns the shortest GrammaticalExpression which expresses that Meaning

    Returns:
        sum of the length of the shortest LoT expression for each meaning in the language
    """
    return aggregate_expression_complexity(
        language, lambda expr: len(expressions_by_meaning[expr.meaning])
    )



def dist(m1: QuantifierModel, m2: QuantifierModel) -> int:
    return sum(
       max(0, m2_zone - m1_zone) 
       for (m1_zone, m2_zone) in zip(m1.zones(), m2.zones())
    )

def utility(m1: QuantifierModel, m2: QuantifierModel) -> float:
    return 1 / (1 + dist(m1, m2))


prior = quantifiers_universe.prior_numpy
utility_matrix =  build_pairwise_matrix(quantifiers_universe, utility)

def comm_cost(language: Language) -> float:
    """Get C(L) := 1 - informativity(L).
    Passes in the prior from `quantifiers_universe` to ultk's informativity calculator.
    """
    return 1 - informativity(language, prior, utility_matrix)
