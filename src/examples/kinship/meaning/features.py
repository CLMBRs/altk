"""Referent-like (but not recursive) data structure storing individuals as bundles of features."""

from .structure import domain, kinship_structure

characteristic = lambda p, x: {y for y in domain if kinship_structure.evaluate(p, x, y)}

feature_dict = {
    e: {
        # truth value
        "is_male": kinship_structure.evaluate("is_male", e),
        # set of entities
        "is_parent": characteristic("is_parent", e),
        "is_older": characteristic("is_older", e),
        "is_sibling_excl": characteristic("is_sibling_excl", e),
    }
    for e in domain
}
