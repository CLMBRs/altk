from ultk.effcomm.informativity import informativity
from ultk.language.grammar import GrammaticalExpression
from ultk.language.language import Language, aggregate_expression_complexity
from ultk.language.semantics import Meaning

from kinship.meaning import universe as kinship_universe


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


prior = kinship_universe.prior_numpy


# TODO: KR use surprisal (bits) as comm_cost. We're just using int(speaker ref == listener ref)
# NOTE: KR use average of costs for each of Alice and Bob. This is because kinship systems differ based on the gender of Ego.
# NOTE: It also seems that KR2012 assumed that each individual belonged to at most one category (word), but this is not the general case!
def comm_cost(language: Language) -> float:
    """Get C(L) := 1 - informativity(L).
    Passes in the prior from `kinship_universe` to ultk's informativity calculator.
    """
    return 1 - informativity(language, prior)