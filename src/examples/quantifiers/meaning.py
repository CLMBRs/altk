from itertools import chain, combinations, permutations, product
from typing import Iterable, Iterator
from ultk.language.semantics import Universe, Meaning, Referent


class QuantifierModel(Referent):
    """A QuantifierModel represents a tuple <M, A, B> where A, B are subsets of M."""

    def __init__(self, M: list, A: frozenset, B: frozenset, name: str):
        super().__init__(name, M=M, A=A, B=B)

    def __str__(self) -> str:
        return (
            f"Quantifier model: {self.name}\n"
            f"\tM: {set(self.M)}\n"
            f"\tA: {set(self.A)}\n"
            f"\tB: {set(self.B)}"
        )

    def __hash__(self) -> int:
        return hash((self.M, self.A, self.B))

    def zones(self) -> tuple[int, int, int, int]:
        """Return the zones (via the name) as a tuple of four integers."""
        return tuple(map(int, self.name.strip("()").split(", ")))


def powerset(iterable) -> Iterable:
    """See itertools recipes:
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def all_models_up_to_size(max_size: int) -> Universe:
    """Generate all isomorphically unique quantifier models up to a specified maximum size.

    Args:
        max_size (int): The maximum size of the model universe.

    Returns:
        Universe: A collection of isomorphically unique quantifier models.
    """

    def canonical_form(
        model: tuple[frozenset[int], frozenset[int], frozenset[int]]
    ) -> tuple[int, int, int, int]:
        """
        Calculate the canonical form of a model using cardinalities of the four sets:
        A ∩ B, A \ B, B \ A, and M \ (A ∪ B).

        Args:
            model (tuple): A tuple representing the universe (`M`) and subsets (`A`, `B`).

        Returns:
            tuple: The canonical form as a tuple of four integers representing the cardinalities
                   of the four key subsets.
        """
        M, A, B = model
        intersection = A & B
        a_minus_b = A - B
        b_minus_a = B - A
        complement = set(M) - (A | B)
        return (len(intersection), len(a_minus_b), len(b_minus_a), len(complement))

    def generate_all_unique_referents(max_size: int) -> Iterator["QuantifierModel"]:
        """
        Generate all isomorphically unique quantifier models up to a specified maximum size.

        Args:
            max_size (int): The maximum size of the model universe.

        Yields:
            QuantifierModel: A quantifier model represented by a universe of objects (`M`)
                             and two subsets (`A`, `B`), along with a canonical representation.

        Notes:
            - Models are deduplicated using the canonical form derived from the cardinalities of
              four sets: A ∩ B, A \ B, B \ A, and M \ (A ∪ B).
        """
        seen_forms = set()
        for model_size in range(max_size):
            objects = range(model_size)
            for M in permutations(objects):
                for A, B in product(powerset(M), repeat=2):
                    model = (frozenset(M), frozenset(A), frozenset(B))
                    canonical = canonical_form(model)
                    if canonical not in seen_forms:
                        seen_forms.add(canonical)
                        yield QuantifierModel(
                            frozenset(M), frozenset(A), frozenset(B), str(canonical)
                        )

    return Universe(tuple(sorted(generate_all_unique_referents(max_size))))


universe = all_models_up_to_size(7)


if __name__ == "__main__":
    print(len(all_models_up_to_size(7)))  # 8 was too many
