from collections.abc import Mapping
from typing import Generic, TypeVar
from frozendict import frozendict

K = TypeVar("K")
V = TypeVar("V")


# TODO: why is mypy still complaining about type arguments in references to this class?
class FrozenDict(frozendict[K, V], Generic[K, V]):

    def setdefault(self, key, default=None):
        raise TypeError("FrozenDict is immutable")
