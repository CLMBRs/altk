import numpy as np
from ultk.language.semantics import Referent, Universe
from dataclasses import dataclass, field
import numpy as np
from ultk.language.grammar import GrammaticalExpression

# Define the mapping from characters to indices
char_to_index = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4}
# Convert characters to indices
one_hot_matrix = np.eye(len(char_to_index))
compositional_matrix = np.array([[1, 0, 1], [0, 1, 1], [1, 1, 1], [0, 0, 1], [0, 0, 0]])


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
        match self.name:
            case str():
                pass
            case np.ndarray():
                new_name = "".join([str(x) for x in self.name])
                object.__setattr__(self, "name", new_name)
            case _:
                raise ValueError("The name must be a string or a numpy array")
        object.__setattr__(
            self,
            "A",
            frozenset([i for i, x in enumerate(self.name) if x in ["0", "2"]]),
        )
        object.__setattr__(
            self,
            "B",
            frozenset([i for i, x in enumerate(self.name) if x in ["1", "2"]]),
        )
        object.__setattr__(
            self,
            "M",
            frozenset(
                [i for i, x in enumerate(self.name) if x in ["0", "1", "2", "3"]]
            ),
        )

    @classmethod
    def from_sets(cls, M: set | frozenset, A: set | frozenset, B: set | frozenset):
        return cls(name=None, M=frozenset(M), A=frozenset(A), B=frozenset(B))

    def get_cardinalities(self) -> dict:
        return {
            "M": len(self.M),
            "A": len(self.A),
            "B": len(self.B),
        }

    def binarize(self, mode="B") -> np.ndarray:
        """
        Binarizes the sequence of characters in the name attribute.

        Returns:
            np.ndarray: An array of binary values, where 1 represents characters '1' or '2', and 0 represents other characters.
        """
        if mode == "B":
            return np.array([1 if char in {"1", "2"} else 0 for char in self.name])
        if mode == "A":
            return np.array([1 if char in {"0", "2"} else 0 for char in self.name])
        if mode == "both":
            return np.array([1 if char in {"2"} else 0 for char in self.name])
        if mode == "B_only":
            return np.array([1 if char in {"1"} else 0 for char in self.name])
        if mode == "A_only":
            return np.array([1 if char in {"0"} else 0 for char in self.name])
        elif mode == "one_hot":
            # Create an identity matrix and select rows corresponding to indices
            indices = [char_to_index[char] for char in self.name]
            one_hot_encoded = one_hot_matrix[indices]
            return one_hot_encoded
        elif mode == "composition":
            indices = [char_to_index[char] for char in self.name]
            one_hot_encoded = compositional_matrix[indices]
            return one_hot_encoded

    def to_numpy(
        self,
        mode="one_hot",
        quantifier_index: np.ndarray | None = None,
        in_meaning: bool = False,
    ):
        """
        Converts the quantifier to a numpy array.
        There are two ways to represent the quantifier:
        1. Using quantifier_index, a one-hot vector that represents the quantifier is concatenated to the end of the quantifier vector.
        2. Using in_meaning, a binary value is concatenated to the end of the quantifier vector. True = 1.
        If you supply quantifier_index, in_meaning is ignored.

        Args:
            quantifier_index (np.ndarray | None, optional): The index of the quantifier to convert.
                If None, all quantifiers are converted. Defaults to None.
            in_meaning (bool, optional): If True, the quantifier is in the meaning space.
                If False, the quantifier is in the expression space. Defaults to False.

        Returns:
            np.ndarray: The quantifier converted to a numpy array.
        """

        one_hot_array = self.binarize(mode=mode)

        # If quantifier_index is provided, concatenate it to each vector in one_hot_array
        if quantifier_index is not None:
            # Ensure quantifier_index is an array
            quantifier_index = np.asarray(quantifier_index)
            if quantifier_index.ndim == 1:
                # Concatenate quantifier_index to each vector
                quantifier_index = quantifier_index.reshape(1, -1).repeat(
                    len(one_hot_array), axis=0
                )
                one_hot_array = np.hstack((one_hot_array, quantifier_index))
            else:
                raise ValueError(
                    "quantifier_index must be a one-dimensional one-hot vector."
                )
        else:
            appended_value = 0
            if in_meaning:
                appended_value = 1
            new_column = np.full((one_hot_array.shape[0], 1), appended_value)

            # Concatenate the new column to the original array
            one_hot_array = np.hstack((one_hot_array, new_column))

        return one_hot_array


@dataclass(frozen=True)
class QuantifierUniverse(Universe):

    m_size: int
    x_size: int

    def __init__(self, referents, m_size, x_size):
        prior = Universe._calculate_prior(referents)
        super().__init__(referents, prior)
        object.__setattr__(self, "m_size", m_size)
        object.__setattr__(self, "x_size", x_size)

    def __add__(self, other):
        """Returns the union of two QuantifierUniverses.
        Largest x_size is used if different."""
        assert self.x_size == other.x_size
        x_size = max(self.x_size, other.x_size)
        return QuantifierUniverse(
            referents=self.referents + other.referents,
            m_size=self.m_size,
            x_size=x_size,
        )

    def get_names(self) -> list[str]:
        """Get the names of the referents in the loaded quantifier universe.

        Returns:
            list: List of names of referents in the quantifier universe.
        """
        return [referent.name for referent in self.referents]

    def binarize_referents(self, mode="B") -> np.ndarray:
        return np.array([referent.binarize(mode=mode) for referent in self.referents])


import random


def summarize_expression(expression: GrammaticalExpression):
    print(str(expression))
    sample = random.sample(list(expression.meaning.mapping), 10)
    for model in sample:
        print(model, expression.meaning.mapping[model])
