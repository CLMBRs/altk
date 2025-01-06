from ultk.effcomm.informativity import informativity
from ultk.language.grammar import GrammaticalExpression, Grammar
from ultk.language.language import Language, aggregate_expression_complexity, Expression
from ultk.language.semantics import Meaning

from .meaning import universe as connectives_universe


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


prior = connectives_universe.prior_numpy


# TODO: Uegaki (2022) includes sophisticated scalar inference in informativity. For now, we just assume bayesian pragmatic listener.
def comm_cost(language: Language) -> float:
    """Get C(L) := 1 - informativity(L).
    Passes in the prior from `connectives_universe` to ultk's informativity calculator.
    """
    return 1 - informativity(language, prior, agent_type="pragmatic")


def swap_p_q(input_string):
    return input_string.translate(str.maketrans("PQ", "QP"))


def commutative(gr_expr: Expression, grammar: Grammar) -> bool:
    original_meaning = gr_expr.evaluate(connectives_universe)
    # this is a little hacky
    expr_swapped = str(gr_expr).translate(str.maketrans("PQ", "QP"))
    gr_expr_swapped = grammar.parse(expr_swapped)
    candidate_meaning = gr_expr_swapped.evaluate(connectives_universe)

    return original_meaning == candidate_meaning


def commutative_only(language: Language, grammar: Grammar) -> bool:
    return all(commutative(e, grammar) for e in language.expressions)
