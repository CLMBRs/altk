from ultk.language.semantics import Referent
from kinship.structure import kinship_structure

from typing import Callable


UnaryPredicate = Callable[[Referent], bool]
BinaryPredicate = Callable[[Referent], Callable[[Referent], bool]]
NullPredicate = Callable[[Referent], bool]

# <<e, t>,t>
ett = Callable[[UnaryPredicate], bool]

# Terminal Rules = Unary Primitives
# bool -> r
# def is_male(x: Referent) -> bool:
#     return kinship_structure.evaluate("is_male", x)

# P -> r
def is_male(x: Referent) -> NullPredicate:
    return lambda _: kinship_structure.evaluate("is_male", x)

# bool -> r
# def is_female(x: Referent) -> bool:
#     return not kinship_structure.evaluate("is_male", x)

# P -> r
def is_female(x: Referent) -> NullPredicate:
    return lambda _: not kinship_structure.evaluate("is_male", x)

# P -> r
def parent(x: Referent, ) -> UnaryPredicate:
    return lambda y: kinship_structure.evaluate("is_parent", x, y)

def child(x: Referent, ) -> UnaryPredicate:
    return lambda y: kinship_structure.evaluate("is_parent", y, x)

def older(x: Referent, ) -> UnaryPredicate:
    return lambda y: kinship_structure.evaluate("is_older", x, y)

def younger(x: Referent, ) -> UnaryPredicate:
    return lambda y: kinship_structure.evaluate("is_older", y, x)

# Nonterminal rulesx    

# # bool -> r P
# def _apply(x: Referent, a: UnaryPredicate,) -> bool:
#     return a(x)

# Nonterminal rule: Fixes a Referent and returns a function to apply predicates

# # ETT -> r
# def _apply(x: Referent) -> ett:
#     """
#     Takes a Referent and returns a lambda function that takes a predicate
#     and applies the Referent to it.
#     """
#     return lambda predicate: predicate(x)

# def rec(x: UnaryPredicate, y: UnaryPredicate) -> UnaryPredicate:
#     return lambda z: x(y(z))


# # bool -> ETT
# def apply_ref(x: ett, a: UnaryPredicate) -> bool:
#     return x(a) # this is actually a(x)

# # bool -> U
# def my_(a: UnaryPredicate) -> bool:
#     return _apply("Ego")(a)

# bool -> P
def my_(a: UnaryPredicate) -> bool:
    return a("Ego")

# P -> P P
def axy_and_by(a: UnaryPredicate, b: NullPredicate,) -> UnaryPredicate:
    # return lambda x, y: a(x, y) and b(y)
    return lambda y: a(y) and b(y)


# TODO: need to find the missing link as to why arbitrary complex functions can't get picked up. 
# Why can't we have mixed types in the rhs? 
# Is there something about having a Referent in the rhs that breaks things?
# 
