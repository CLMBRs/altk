"""Smaller kinship grammar that minimally generates the expressions necessary for English."""

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


# Technically the KR2012 definition of aunt/uncle includes Mother and Father...
# eet -> e
def exclusive_sibling(*_: e, name="sibling") -> eet:
    def sibling_predicate(x, y):
        # x and y must share at least one parent
        shared_parent = any(
            kinship_structure.evaluate("is_parent", z.name, x.name)
            and kinship_structure.evaluate("is_parent", z.name, y.name)
            for z in universe
        )
        # Exclude self
        return shared_parent and x != y

    return lambda x: lambda y: sibling_predicate(x, y)
