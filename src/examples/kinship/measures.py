from ultk.effcomm.informativity import informativity
from ultk.language.grammar import GrammaticalExpression
from ultk.language.language import Language, aggregate_expression_complexity, Expression
from ultk.language.semantics import Meaning
from .meaning.features import feature_dict

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
def comm_cost(language: Language) -> float:
    """Get C(L) := 1 - informativity(L).
    Passes in the prior from `kinship_universe` to ultk's informativity calculator.
    """
    return 1 - informativity(language, prior)


from typing import Any, Callable

feat_struct = dict[str, bool | set[str]]

def is_between(a: feat_struct, b: feat_struct, c: feat_struct) -> bool:
    """
    Determines if object b is "between" objects a and c based on their features. Specifically, for every feature in a, b, and c, the value of b[feature] matches either a[feature] or c[feature].

    Parameters:
    a (dict): A dictionary representing the features of object a.
    b (dict): A dictionary representing the features of object b.
    c (dict): A dictionary representing the features of object c.

    Returns:
    bool: True if b is "between" a and c for all features, False otherwise.
    """
    for feature in a.keys():  # Assume all objects share the same features
        # Check if b is between a and c for this feature
        if not (b[feature] == a[feature] or b[feature] == c[feature]):
            return False
    return True



# connectedness (modulo exclusivity)
def connected(
    expression: Expression,
    in_between_relation: Callable[[feat_struct, feat_struct, feat_struct], bool] = is_between,
    partial_order: Callable[[Any, Any], bool] = lambda x, y: x == y,
    ) -> bool:
    # Get the set of referents for th expression
    meaning = expression.meaning

    # NOTE: We must search all referents in domain, not just those that are true-like, or connectedness would be trivial.
    referents_list = list(set(m for m in meaning))

    # Connectedness (for e,t functions). A function f of type e,t is connected iff for any
    # objects a, b, and c, if [a b c], then f(b) ≥ f(a) or f(b) ≥ f(c).

    # For all triplets of referents
    for i, a in enumerate(referents_list):
        for j, b in enumerate(referents_list):
            for k, c in enumerate(referents_list):
                if i != j != k:  # Ensure a, b, and c are distinct (nontrivial)

                    if in_between_relation(
                        feature_dict[a.name], 
                        feature_dict[b.name], 
                        feature_dict[c.name],
                    ):
                        # f(b) must satisfy the partial order with f(a) or f(c)
                        if not (
                            partial_order(meaning[b], meaning[a]) 
                            or partial_order(meaning[b], meaning[c])
                        ):
                            breakpoint()
                            return False
    return True

def degree_connected(language: Language) -> float:
    # TODO: rename from complexity to measurer
    return aggregate_expression_complexity(
        language, connected,
    ) / len(language)