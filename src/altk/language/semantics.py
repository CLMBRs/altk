"""Classes for modeling the meanings of a language.

    Meanings are modeled as things which map linguistic forms to objects of reference. The linguistic forms and objects of reference can in principle be very detailed, and future work may elaborate the meaning classes and implement a Form class.

    In efficient communication analyses, simplicity and informativeness can be measured as properties of semantic aspects of a language. E.g., a meaning is simple if it is easy to represent, or to compress into some code; a meaning is informative if it is easy for a listener to recover a speaker's intended literal meaning.

    Examples:

        >>> from altk.language.semantics import Referent, Meaning, Universe
        >>> from altk.language.language import Expression
        >>> # construct the meaning space for numerals
        >>> numerals_universe = NumeralUniverse(referents=[NumeralReferent(str(i)) for i in range(1, 100)])
        >>> # construct a list of referents for the expression 'a few'
        >>> a_few_refs = [NumeralRefernt(name=str(i)) for i in range(2, 6)]
        >>> a_few_meaning = NumeralMeaning(referents=a_few_refs, universe=numerals_universe)
        >>> # define the expression
        >>> a_few = NumeralExpression(form="a few", meaning=a_few_meaning)
"""

from typing import Iterable


class Referent:
    """A referent is some object in the universe for a language."""

    def __init__(self, name: str, properties: dict = {}, **kwargs) -> None:
        """Initialize a referent.

        Args:
            name: a string representing the name of the referent
        """
        self.name = name
        self.__dict__.update(properties, **kwargs)

    def __str__(self) -> str:
        return str(self.__dict__)


class Universe:

    """The universe is the set of possible referent objects for a meaning."""

    def __init__(self, referents: Iterable[Referent]):
        self.referents = referents

    def __str__(self):
        referents_str = ",\n".join([str(point) for point in self.referents])
        return f"Universe: {referents_str}"

    def __eq__(self, __o: object) -> bool:
        """Returns true if the two universes are the same set."""
        return self.referents == __o.referents

    def __len__(self) -> int:
        return len(self.referents)


class Meaning:

    """A meaning picks out a set of objects from the universe.

    On one tradition (from formal semantics), we might model an underspecified meaning as a subset of the universe. Sometimes these different referents are not equally likely, in which it can be helpful to define a meaning explicitly as a distribution over the universe.
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

    def __eq__(self, other):
        return (self.referents, self.universe) == (other.referents, other.universe)
