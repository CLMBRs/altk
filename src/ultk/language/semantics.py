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
            for feature in ref.__dict__:
                if feature != "name": #Axes should not include the name
                    if feature not in axes:
                        axes[feature] = set()
                    axes[feature].add(ref.__dict__[feature])
        for key in axes:
            axes[key] = sorted(list(axes[key]))
        return dict(sorted(axes.items()))
    

    
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
        """
        Returns the set of referents that compose the Meaning as a dict. 
        """
        return {"referents": [referent.to_dict() for referent in self.referents]}
    
    def to_array(self) -> np.ndarray:
        """Converts the meaning to an feature axis-indexed numpy array.
        
        The first dimension of the numpy array corresponds to the first feature, the second dimension corresponds to the second feature, and so on. """
        axes = self.universe.axes_from_referents()
        axis_keys = list(axes.keys())
        axis_values = list(axes.values())
        len_array = tuple(len(property_set) for property_set in axis_values)
        a = np.zeros(len_array)

        for referent in self.referents:
            properties = referent.__dict__
            prop_count = 0
            indices = [0] * len(axes) 
            for property in properties.keys():
                if property != "name": #Disregard name property
                    if(property not in axis_keys):
                        raise KeyError("Property of the Meaning does not exist in the Universe.")
                    property_index = axis_keys.index(property)
                    indices[property_index] = axis_values[property_index].index(properties[property])
                    print("Property: {} Referent: {} Index:{}".format(property, referent, indices))
            print("array: " + str(a))
            a[tuple(indices)] = 1 
        return a
    


    def __bool__(self):
        return bool(self.referents) and bool(self.universe)

    def __eq__(self, other):
        return (self.referents, self.universe) == (other.referents, other.universe)

    def __str__(self):
        return f"Referents:\n\t{','.join(str(referent) for referent in self.referents)}\
            \nDistribution:\n\t{self.dist}\n"

    def __hash__(self):
        return hash(tuple(self.referents))
