from ultk.language.semantics import Referent
from kinship.structure import kinship_structure
from kinship.meaning import Ego, universe

from typing import Callable


t = bool
e = Referent
et = Callable[[e], t]
eet = Callable[[e], et]
arg = tuple[e]

start = t


# have to hack a dummy arg because rules aren't considered terminal unless they take Referents
# et -> e
def male(*_: e) -> et: 
    return lambda y: kinship_structure.evaluate("is_male", y.name)

def female(*_: e) -> et: 
    return lambda y: not kinship_structure.evaluate("is_male", y.name)

# need to bind args for intermediate node
# arg -> e ...
def bind(*a: e, name=".") -> arg:
    return a

# t -> et arg
def apply_et(p: et, a: arg, name="*") -> t:
    return p(*a)

# eet -> e
def parent(*_: e) -> eet:
    return lambda x: lambda y: kinship_structure.evaluate("is_parent", x.name, y.name)

# eet -> e
def child(*_: e) -> eet:
    return lambda x: lambda y: kinship_structure.evaluate("is_parent", y.name, x.name)

# et -> eet arg
def apply_eet(p: eet, a: arg, name="**") -> et:
    return p(*a)

# et -> eet
# def _my(a: eet, ) -> et:
    # return lambda _: a(_)(Ego)

def _my_exclusive(a: eet, name="my_x") -> et:
    return lambda x: a(x)(Ego) and x != Ego

# et -> eet
def _flip_xy(a: eet, name="flip") -> eet:
    return lambda x: lambda y: a(y)(x)


# et -> eet et
def axy_and_by(a: eet, b: et,) -> eet:
    return lambda x: lambda y: a(x)(y) and b(y)

# et -> eet e
def axy_and_bx(a: eet, b: et) -> eet:
    return lambda x: lambda y: a(x)(y) and b(x)

# eet -> eet eet
def axy_and_bxy(a: eet, b: eet) -> eet:
    return lambda x: lambda y: a(x)(y) and b(x)(y)

# ∃z( A(x,z) ^ B(z, y) )
# eet -> eet eet
def exists_z_and(a: eet, b: eet) -> eet:
    return lambda x: lambda y: any( z for z in universe if a(x)(z) and b(z)(y) )