"""Grammar with disconnected primitives."""

from ultk.language.semantics import Referent
from examples.kinship.meaning.structure import kinship_structure
from examples.kinship.meaning import Ego, universe

from typing import Callable


t = bool
e = Referent
et = Callable[[e], t]
eet = Callable[[e], et]
arg = tuple[e]

start = t

##############################################################################
# Bind/Apply logic
##############################################################################


# Unwrap args and apply predicate
# t -> et arg
def apply_et(p: et, a: arg, name="*") -> t:
    return p(*a)


# Bind args for intermediate node
# arg -> e ...
def bind(*a: e, name=".") -> arg:
    return a


# For disconnected predicates
def grarent(*_: e) -> eet:
    return lambda x: lambda y: kinship_structure.evaluate("is_parent", x.name, y.name) and x.name != "Paternal_Younger_Brother"

def gremale(*_: e) -> et:
    return lambda x: not kinship_structure.evaluate("is_male", x.name) and x.name != "Paternal_Younger_Sister"





# et -> eet
def my_exclusive(a: eet, name="my_") -> et:
    return lambda x: a(x)(Ego) and x != Ego


# et -> eet et
def axy_and_by(
    a: eet,
    b: et,
) -> eet:
    return lambda x: lambda y: a(x)(y) and b(y)


# et -> eet et
def axy_and_bx(a: eet, b: et) -> eet:
    return lambda x: lambda y: a(x)(y) and b(x)


# ∃z( A(x,z) ^ B(z, y) )
# eet -> eet eet
def Ez_axz_and_bzy(a: eet, b: eet) -> eet:
    return lambda x: lambda y: any(z for z in universe if a(x)(z) and b(z)(y))


