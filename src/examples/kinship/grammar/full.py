"""Full grammar from Kemp and Regier (2012)."""

from examples.kinship.grammars.small import *


# et -> eet et
def axy_or_by(a: eet, b: et) -> eet:
    return lambda x: lambda y: a(x)(y) or b(y)


# et -> eet et
def axy_or_bx(a: eet, b: et) -> eet:
    return lambda x: lambda y: a(x)(y) or b(x)


# eet -> eet eet
def axy_or_bxy(a: eet, b: eet) -> eet:
    return lambda x: lambda y: a(x)(y) or b(x)(y)


# et -> eet
def flip_xy(a: eet, name="flip") -> eet:
    return lambda x: lambda y: a(y)(x)


# eet -> eet
def sym(a: eet, name="<->") -> eet:
    return lambda x: lambda y: a(x)(y) or a(y)(x)


# transitive closure, e.g. 'ancestor-of'
# eet -> eet
def tr_cl(a: eet) -> eet:
    def closure(x, y):
        # Base case: direct relationship exists
        if a(x)(y):
            return True
        # Recursive case: check for intermediary z
        return any(a(x)(z) and closure(z, y) for z in kinship_structure.domain)

    return closure
