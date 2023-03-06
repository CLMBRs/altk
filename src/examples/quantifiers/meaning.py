from itertools import chain, combinations, permutations, product
from typing import Iterable
from altk.language.semantics import Universe, Meaning, Referent


class QuantifierModel(Referent):
    """A QuantifierModel represents a tuple <M, A, B> where A, B are subsets of M."""

    def __init__(self, M: list, A: set, B: set, name: str = "QuantifierModel"):
        super().__init__(name)
        assert A <= set(M)
        assert B <= set(M)
        self.M = M
        self.A = A
        self.B = B

    def __str__(self) -> str:
        return f"Quantifier model: {self.name}\n\tM: {self.M}\n\tA: {self.A}\n\tB: {self.B}"

    def __hash__(self) -> int:
        return hash((self.M, self.A, self.B))

    def __eq__(self, other):
        return isinstance(other, type(self)) and (self.M, self.A, self.B) == (
            other.M,
            other.A,
            other.B,
        )


def powerset(iterable) -> Iterable:
    """See itertools recipes:
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def all_models_up_to_size(max_size: int) -> Universe:
    def all_referents(max_size: int):
        for model_size in range(max_size):
            objects = range(model_size)
            for M in permutations(objects):
                for A, B in product(powerset(M), powerset(M)):
                    yield QuantifierModel(M, set(A), set(B))

    return Universe(all_referents(max_size))

if __name__ == '__main__':
    print(all_models_up_to_size(3))
