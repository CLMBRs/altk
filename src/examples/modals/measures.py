from ultk.language.language import (
    Language,
    Expression,
    Meaning,
    Referent,
    aggregate_expression_complexity,
)
from ultk.language.grammar import GrammaticalExpression
from ultk.effcomm.informativity import informativity, build_pairwise_matrix

from .meaning import universe as modals_universe


def half_credit_utility(m: Referent, m_: Referent) -> float:
    score = 0.0
    if m.force == m_.force:
        score += 0.5
    if m.flavor == m_.flavor:
        score += 0.5
    return score


half_credit_util_matrix = build_pairwise_matrix(
    modals_universe,
    half_credit_utility,
)


def comm_cost(language: Language) -> float:
    return 1 - informativity(
        language, modals_universe.prior_numpy, half_credit_util_matrix
    )


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


def iff(e: Expression) -> bool:
    """Whether an expression satisfies the Independence of Force and Flavor Universal.

    The set of forces X that a modal lexical item m can express and the set of flavors be Y that m can express, then the full set of meaning points that m expresses is the Cartesian product of X and Y.
    """
    points = {(ref.force, ref.flavor) for ref in e.meaning if e.meaning[ref]}
    forces, flavors = zip(*points)
    return all(
        (force, flavor) in points for force in set(forces) for flavor in set(flavors)
    )
