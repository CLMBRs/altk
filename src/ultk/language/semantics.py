"""Classes for modeling the meanings of a language.

    Meanings are modeled as things which map linguistic forms to objects of reference. The linguistic forms and objects of reference can in principle be very detailed, and future work may elaborate the meaning classes and implement a Form class.

    In efficient communication analyses, simplicity and informativeness can be measured as properties of semantic aspects of a language. E.g., a meaning is simple if it is easy to represent, or to compress into some code; a meaning is informative if it is easy for a listener to recover a speaker's intended literal meaning.

    Examples:

        >>> from ultk.language.semantics import Referent, Meaning, Universe
        >>> from ultk.language.language import Expression
        >>> # construct the meaning space for numerals
        >>> numerals_universe = NumeralUniverse(referents=[NumeralReferent(str(i)) for i in range(1, 100)])
        >>> # construct a list of referents for the expression 'a few'
        >>> a_few_refs = [NumeralReferent(name=str(i)) for i in range(2, 6)]
        >>> a_few_meaning = NumeralMeaning(referents=a_few_refs, universe=numerals_universe)
        >>> # define the expression
        >>> a_few = NumeralExpression(form="a few", meaning=a_few_meaning)
"""

from itertools import product
from typing import Iterable, Union
import numpy as np
import pandas as pd


class Referent:
    """A referent is some object in the universe for a language."""

    def __init__(self, name: str, properties: dict = {}, **kwargs) -> None:
        """Initialize a referent.

        Args:
            name: a string representing the name of the referent
        """
        self.name = name
        self.__dict__.update(properties, **kwargs)

    def to_dict(self) -> dict:
        return self.__dict__

    def __str__(self) -> str:
        return str(self.__dict__)

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.__dict__)))


class Universe:

    """The universe is the set of possible referent objects for a meaning."""

    def __init__(self, referents: Iterable[Referent], prior: dict[str, float] = None):
        self.referents = referents
        self._referents_by_name = {referent.name: referent for referent in referents}
        # set to uniform prior if none specified
        size = len(referents)
        prior = prior or {referent.name: 1 / size for referent in referents}
        self.set_prior(prior)

    def set_prior(self, prior: dict[str, float]):
        self._prior = prior

    def prior_numpy(self) -> np.ndarray:
        return np.array([self._prior[referent.name] for referent in self.referents])
    
    def axes_from_referents(self) -> dict:
        """Generates the feature axes, and their covering values from the set of all Referents in the Universe. 
        This may omit unspecified feature values that are possible but don't exist in the dataset. """
        axes = dict()
        for ref in self.referents:
            for feature, value in ref.properties:
                if feature not in axes:
                    axes[feature] = set()
                axes[feature].add(value)
        return axes
    
    def array_to_points(self, a: np.ndarray) -> set:
        """Converts a numpy array to a set of points.

        Args:
            a: numpy array representing a modal meaning.

        Raises:
            ValueError: if the meaning space doesn't match the array shape.axis 0 (rows) are forces, axis 1 (columns) are flavors.
        """
        if a.shape != tuple([len(features) for axis, features in self.axes_from_referents()]):
            raise ValueError(
                f"The size of the numpy array must match the size of the modal meaning space. a.shape={a.shape}, self.axes={self.axes_from_referents()}"
            )

        # return {
        #     ModalMeaningPoint(name=f"{self.forces[pair[0]]}+{self.flavors[pair[1]]}")
        #     for pair in np.argwhere(a)
        # }
        return {
            Referent(force=self.forces[pair[0]], flavor=self.flavors[pair[1]])
            for pair in np.argwhere(a)
        }
    
    def generate_meanings(self) -> list:
        """Generates all possible subsets of the meaning space, based on the pre-existing axes."""
        shape = tuple([len(features) for axis, features in self.axes_from_referents()])
        arrs = [
            np.array(i).reshape(shape)
            for i in product([0, 1], repeat=len(self.referents))
        ]
        arrs = arrs[1:]  # remove the empty array meaning to prevent div by 0
        meanings = [ModalMeaning(self.array_to_points(arr), self) for arr in arrs]
        return meanings
    
    def __getitem__(self, key: Union[str, int]) -> Referent:
        if type(key) is str:
            return self._referents_by_name[key]
        elif type(key) is int:
            return self.referents[key]
        else:
            raise KeyError("Key must either be an int or str.")

    def __str__(self):
        referents_str = ",\n\t".join([str(point) for point in self.referents])
        return f"Points:\n\t{referents_str}\nDistribution:\n\t{self._prior}"

    def __eq__(self, __o: object) -> bool:
        """Returns true if the two universes are the same set."""
        # TODO: may want to generalize to checking additional structure.  Or just leave that to sub-classes?
        return set(self.referents) == set(__o.referents)

    def __len__(self) -> int:
        return len(self.referents)

    def __hash__(self) -> int:
        return hash(tuple(self.referents))

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame):
        """Build a Universe from a DataFrame.
        It's assumed that each row specifies one Referent, and each column will be a property
        of that Referent.  We assume that `name` is one of the columns of the DataFrame.

        Args:
            a DataFrame representing the meaning space of interest, assumed to have a column `name`
        """
        prior = None
        if "probability" in df.columns:
            prior = dict(zip(df["name"], df["probability"]))
        records = df.to_dict("records")
        referents = tuple(Referent(record["name"], record) for record in records)
        return cls(referents, prior)

    @classmethod
    def from_csv(cls, filename: str):
        """Build a Universe from a CSV file.  This is a small wrapper around
        `Universe.from_dataframe`, so see that documentation for more information.
        """
        df = pd.read_csv(filename)
        return cls.from_dataframe(df)


class Meaning:
    """A meaning picks out a set of objects from the universe.

    On one tradition (from formal semantics), we might model an underspecified meaning as a subset of the universe.
    Sometimes these different referents are not equally likely,
    in which it can be helpful to define a meaning explicitly as a distribution over the universe.
    """

    def __init__(
        self,
        referents: Iterable[Referent],
        universe: Universe,
        dist: dict[str, float] = None,
    ) -> None:
        """A meaning is the set of things it refers to.

        The objects of reference are a subset of the universe of discourse. Sometimes it is natural to construe the meaning as as a probability distribution over the universe, instead of just a binary predicate.

        Args:
            referents: a list of Referent objects, which must be a subset of the referents in `universe`.

            universe: a Universe object that defines the probability space for a meaning.

            dist: a dict of with Referent names as keys and weights or probabilities as values, representing the distribution over referents to associate with the meaning. By default is None, and the distribution will be uniform over the passed referents, and any remaining referents are assigned 0 probability.
        """
        if not set(referents).issubset(set(universe.referents)):
            print("referents:")
            print([str(r) for r in referents])
            print("universe:")
            print([str(r) for r in universe.referents])
            raise ValueError(
                f"The set of referents for a meaning must be a subset of the universe of discourse."
            )

        self.referents = referents
        self.universe = universe

        zeros = {
            ref.name: 0.0 for ref in set(self.universe.referents) - set(self.referents)
        }
        if dist is not None:
            # normalize weights to distribution
            total_weight = sum(dist.values())
            self.dist = {
                ref.name: dist[ref.name] / total_weight for ref in self.referents
            } | zeros

        else:
            self.dist = {
                ref.name: 1 / len(self.referents) for ref in self.referents
            } | zeros

    def to_dict(self) -> dict:
        return {"referents": [referent.to_dict() for referent in self.referents]}

    def __bool__(self):
        return bool(self.referents) and bool(self.universe)

    def __eq__(self, other):
        return (self.referents, self.universe) == (other.referents, other.universe)

    def __str__(self):
        return f"Referents:\n\t{','.join(str(referent) for referent in self.referents)}\
            \nDistribution:\n\t{self.dist}\n"

    def __hash__(self):
        return hash(tuple(self.referents))
