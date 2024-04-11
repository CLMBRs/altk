
from typing import Iterable, Union
import numpy as np
import pandas as pd
from ultk.language.semantics import Referent, Universe
from dataclasses import dataclass, field
from concepts.contexts import Context

@dataclass(eq=True, frozen=True)
class QuantifierModel(Referent):
    """A quantifier model is a single referent that captures a particular interpretation of a quantifier meaning, which is a set of quantifier referents.

    Every quantifier model is a quadruple <M, A, B>, where M corresponds to all possible quantifier referents for a given communicative situation, A and B are differents sets of quantifier referents that correspond to the items of comparison in quantificational logic.
    
    X denotes the set of all possible quantifier referents in a given Universe. A and B are subsets of M and each of M, A, and B are subsets of X. 

    For the purposes of this project, a QuantifierModel is a Referent (capital R), but the individual referents for a given model are the indices of the QuantifierModel's sets.

    0 => A
    1 => B
    2 => A | B
    3 => M - (A | B)
    4 => X - (M | A | B)
    
    """

    name: str = None
    M: frozenset = field(init=False)
    A: frozenset = field(init=False)
    B: frozenset = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'A', frozenset([i for i, x in enumerate(self.name) if x in ['0','2']]))
        object.__setattr__(self, 'B', frozenset([i for i, x in enumerate(self.name) if x in ['1','2']]))
        object.__setattr__(self, 'M', frozenset([i for i, x in enumerate(self.name) if x in ['0','1','2','3']]))

    @classmethod
    def from_sets(cls, M: set | frozenset, A: set | frozenset, B: set | frozenset):
        return cls(name=None, M=frozenset(M), A=frozenset(A), B=frozenset(B))

    def get_cardinalities(self) -> dict:
        return {"M": len(self.M), 
                "A": len(self.A), 
                "B": len(self.B), 
                }


class QuantifierUniverse(Universe):

    def __init__(self, referents: Iterable[QuantifierModel], m_size: int = None, x_size: int = None, prior: dict[str, float] = None):
        super().__init__(referents, prior)
        self.m_size = m_size
        self.x_size = x_size
    
    def __add__(self, other):
        """Returns the union of two QuantifierUniverses.
        Largest x_size is used if different."""
        assert self.x_size == other.x_size
        x_size = max(self.x_size, other.x_size)
        return QuantifierUniverse(list(set(self.referents) | set(other.referents)), prior={**self._prior, **other._prior}, x_size=x_size)


