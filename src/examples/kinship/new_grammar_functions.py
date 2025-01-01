from ultk.language.semantics import Referent
from kinship.structure import kinship_structure
from kinship.meaning import Ego

from typing import Callable



S = bool
a = Referent

P1 = Callable[[a], S]
P2 = Callable[[a, a], S]

B1 = tuple[a]
B2 = tuple[a, a]

start = S



# P1 -> a a
def _parent(*_: a) -> P2:
    return lambda x, y: kinship_structure.evaluate("is_parent", x.name, y.name)

# P1 -> a
def _male(*_: a) -> P1:
    return lambda y: kinship_structure.evaluate("is_male", y.name)

# P1 -> P2
def _my(a: P2, ) -> P1:
    return lambda x: a(x, Ego)


# P2 -> P2 P1
def _axy_and_by(
    a: P2, b: P1, name="_and1",) -> P2:
    return lambda x, y: a(x, y) and b(y)



# B1 -> a
def bind_unary_terminal(arg: a, name=".") -> B1:
    return (arg,)

# B2 -> a a
def bind_binary_terminal(arg1: a, arg2: a, name="..") -> B2:
    return (arg1, arg2)

# S -> B1 P1
def evaluate_bound_unary(arg: B1, p: P1, name="*") -> S:
    return p(*arg)


# S -> B2 P2
def evaluate_bound_binary(args: B2, p: P2, name="**") -> S:
    return p(*args)
