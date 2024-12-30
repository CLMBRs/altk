from ultk.language.semantics import Referent
from kinship.structure import kinship_structure

from typing import Callable


BinaryPredicate = Callable[[Referent, Referent], bool]
UnaryPredicate = Callable[[Referent], bool]


# NOTE: a referent of the universe I think should actually be a pair!
# Because it's always in relation to a person. Maybe the pair is always (Ego, X), but still.

# Unary primitives
def is_male(x: Referent) -> bool:
    return kinship_structure.evaluate("is_male", x)

def is_female(x: Referent) -> bool:
    return not kinship_structure.evaluate("is_male", x)

# Binary primitives
def parent(x: Referent, y: Referent) -> bool:
    return kinship_structure.evaluate("is_parent", x, y)

def child(x: Referent, y: Referent) -> bool:
    return kinship_structure.evaluate("is_parent", y, x)

def older(x: Referent, y: Referent) -> bool:
    return kinship_structure.evaluate("is_older", x, y)

def younger(x: Referent, y: Referent) -> bool:
    return kinship_structure.evaluate("is_older", y, x)


# Conjunction
def axy_and_by(a: BinaryPredicate, b: UnaryPredicate,) -> BinaryPredicate:
    return lambda x, y: a(x, y) and b(y)

def axy_and_bx(a: BinaryPredicate, b: UnaryPredicate,) -> BinaryPredicate:
    return lambda x, y: a(x, y) and b(x)

def axy_and_bxy(a: BinaryPredicate, b: BinaryPredicate) -> BinaryPredicate:
    return lambda x, y: a(x, y) and b(x, y)

# Disjunction
def axy_or_by(a: BinaryPredicate, b: UnaryPredicate,) -> BinaryPredicate:
    return lambda x, y: a(x, y) or b(y)

def axy_or_bx(a: BinaryPredicate, b: UnaryPredicate,) -> BinaryPredicate:
    return lambda x, y: a(x, y) or b(x)

def axy_or_bxy(a: BinaryPredicate, b: BinaryPredicate,) -> BinaryPredicate:
    return lambda x, y: a(x, y) or b(x, y)

# Existential
def exists_z(a: BinaryPredicate, b: UnaryPredicate,) -> BinaryPredicate:
    return lambda x, y: any(a(x,z) and b(z, y) for z in kinship_structure.domain)

def flip_xy(a: BinaryPredicate,) -> BinaryPredicate:
    return lambda x, y: a(y, x)

# symmetric
def sym(a: BinaryPredicate,) -> BinaryPredicate:
    return lambda x, y: a(x, y) or a(y, x)

# transitive closure, e.g. 'ancestor-of'
def tr_cl(a: BinaryPredicate) -> BinaryPredicate:
    def closure(x, y):
        # Base case: direct relationship exists
        if a(x, y):
            return True
        # Recursive case: check for intermediary z
        return any(a(x, z) and closure(z, y) for z in kinship_structure.domain)
    return closure
