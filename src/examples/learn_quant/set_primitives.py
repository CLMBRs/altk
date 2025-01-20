from typing import Callable
from ultk.language.semantics import Referent


global start
start = "bool"


class FrozensetA(frozenset):
    def __new__(cls, *args):
        return super().__new__(cls, *args)


class FrozensetB(frozenset):
    def __new__(cls, *args):
        return super().__new__(cls, *args)


def A(r: Referent, weight=10.0) -> "FrozensetA":
    """
    Return the int 0

    Allows for the int 0 to be passed to sequence operations
    such as full() and tok_map().

    Parameter _: any sequence of symbols
    Precondition: Referent
    """
    weight = 10.0
    return FrozensetA(r.A)


def B(r: Referent, weight=10.0) -> "FrozensetB":
    """
    Return the int 1

    Allows for the int 1 to be passed to sequence operations
    such as full() and tok_map().

    Parameter _: any sequence of symbols
    Precondition: Referent
    """
    weight = 10.0
    return FrozensetB(r.B)
