"""Smaller kinship grammar."""

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

# Need to bind args for intermediate node
# arg -> e ...
def bind(*a: e, name=".") -> arg:
    return a

# Then unwrap args and apply predicate
# t -> et arg
def apply_et(p: et, a: arg, name="*") -> t:
    return p(*a)

# et -> eet arg
def apply_eet(p: eet, a: arg, name="**") -> et:
    return p(*a)

##############################################################################
# Terminal rules
##############################################################################

# Using dummy args because grammar rules aren't considered terminal unless they take Referents
# et -> e
def male(*_: e) -> et: 
    return lambda y: kinship_structure.evaluate("is_male", y.name)

def female(*_: e) -> et: 
    return lambda y: not kinship_structure.evaluate("is_male", y.name)

# eet -> e
def parent(*_: e) -> eet:
    return lambda x: lambda y: kinship_structure.evaluate("is_parent", x.name, y.name)

# eet -> e
def child(*_: e) -> eet:
    return lambda x: lambda y: kinship_structure.evaluate("is_parent", y.name, x.name)

##############################################################################
# Nonterminal rules
##############################################################################

# The 'ego_relative' predicate. Use an exclusive version. 
# To get inclusive, in case you want things like 'parent of my child',
# use lambda _: a(_)(Ego)
# et -> eet
def my_exclusive(a: eet, name="my_x") -> et:
    return lambda x: a(x)(Ego) and x != Ego


# et -> eet et
def axy_and_by(a: eet, b: et,) -> eet:
    return lambda x: lambda y: a(x)(y) and b(y)

# et -> eet et
def axy_and_bx(a: eet, b: et) -> eet:
    return lambda x: lambda y: a(x)(y) and b(x)

# eet -> eet eet
def axy_and_bxy(a: eet, b: eet) -> eet:
    return lambda x: lambda y: a(x)(y) and b(x)(y)

# ∃z( A(x,z) ^ B(z, y) )
# eet -> eet eet
def exists_z_and(a: eet, b: eet) -> eet:
    return lambda x: lambda y: any( z for z in universe if a(x)(z) and b(z)(y) )