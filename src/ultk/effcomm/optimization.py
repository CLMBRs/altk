"""Classes and functions for generating languages that optimize the simplicity/informativeness trade-off, e.g. via an iterative evolutionary algorithm."""

from abc import abstractmethod
import copy
import random
import math
from typing import Any, Callable, Type
from tqdm import tqdm
from ultk.effcomm.tradeoff import pareto_optimal_languages
from ultk.language.language import Expression, Language

##############################################################################
# Mutation
##############################################################################

"""Minimal API for defining mutations used by an EvolutionaryOptimizer."""


class Mutation:
    @staticmethod
    @abstractmethod
    def precondition(language: Language, **kwargs) -> bool:
        """Whether a mutation is allowed to apply to a language."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def mutate(language: Language, *args, **kwargs) -> Language:
        """Mutate the language, possibly using a list of expressions."""
        raise NotImplementedError()


class RemoveExpression(Mutation):
    @staticmethod
    def precondition(language: Language, **kwargs) -> bool:
        return len(language) > 1

    @staticmethod
    def mutate(language: Language, expressions: list[Expression], **kwargs) -> Language:
        new_expressions = list(language.expressions)
        new_expressions.pop(random.randrange(len(language)))
        return type(language)(tuple(sorted(new_expressions)))


class AddExpression(Mutation):
    @staticmethod
    def precondition(language: Language, **kwargs) -> bool:
        return True

    @staticmethod
    def mutate(language: Language, expressions: list[Expression], **kwargs) -> Language:
        new_expressions = list(language.expressions)
        new_expressions.append(random.choice(expressions))
        return type(language)(tuple(sorted(new_expressions)))


##############################################################################
# Evolutionary Optimizer
##############################################################################


class EvolutionaryOptimizer:
    """Class for approximating the Pareto frontier of languages optimizing the simplicity/informativity trade-off."""

    def __init__(
        self,
        objectives: list[Callable[[Language], Any]],
        expressions: list[Expression],
        sample_size: int = 0,
        max_mutations: int = 0,
        generations: int = 0,
        lang_size: int | None = None,
        mutations: tuple[Type[Mutation], ...] = (AddExpression, RemoveExpression),
    ):
        """Initialize the evolutionary algorithm configurations. By default, `generations` is 0, so `self.fit(seed_languages)` just estimates the frontier of the passed list of languages.

        The measures of complexity and informativity, the expressions, and the mutations are all specific to the particular semantic domain.

        Args:
            objectives: a dict of the two objectives to optimize for, e.g. simplicity and informativeness, of the form, e.g.
                {
                    "complexity": comp_measure,
                    "comm_cost": lambda l: 1 - inf_measure(l)
                }

            expressions:    a list of expressions from which to apply mutations to languages.


            sample_size:  the size of the population at every generation.

            max_muatations:   between 1 and this number of mutations will be applied to a subset of the population at the end of each generation.

            generations:  how many iterations to run the evolutionary algorithm for.

            lang_size:    between 1 and this number of expressions comprise a language.

            mutations: (optional) a list of Mutation objects, defaults to add/remove expression

            mutation_args: the args that all of the Mutation objects expect
        """
        self.objectives = objectives
        self.expressions = expressions
        self.mutations = mutations

        self.sample_size = sample_size
        self.max_mutations = max_mutations
        self.generations = generations
        # set max lang size to # expressions if none provided
        self.lang_size: int = (
            lang_size or len(expressions) if expressions is not None else None
        )
        self.dominating_languages = None
        self.explored_languages = None

    def fit(
        self,
        seed_population: list[Language],
        explore: float = 0.0,
        front_pbar: bool = False,
    ) -> dict[str, list[Language]]:
        """Computes the Pareto frontier, a set languages which cannot be both more simple and more informative.

        Uses pygmo's nondominated_front method for computing a population's best solutions to a multi-objective optimization problem.

        Args:
            seed_population: a list of languages representing the population at generation 0 of the algorithm.

            explore: a float in [0,1] representing how much to optimize for fitness
                (optimality wrt pareto front of complexity and comm_cost), and how much to randomly explore.

            front_pbar: a bool (default False) indicating whether to display progress every time `pareto_dominant_languages` is called. Useful when the population is large.

        Returns:
            a dict of the estimated optimization solutions, as well as points explored along the way; of the form

                {
                "dominating_languages": list of languages as estimated solutions,
                "explored_languages": list of all the languages explored during the evolutionary algorithm,
                }
        """
        languages = copy.copy(seed_population)
        explored_languages = []

        for _ in tqdm(range(self.generations)):
            # Keep track of visited
            explored_languages.extend(copy.copy(languages))

            # Calculate dominating individuals
            dominating_languages = pareto_optimal_languages(
                languages, self.objectives, unique=True
            )
            # Possibly explore
            parent_languages = sample_parents(
                dominating_languages, explored_languages, explore
            )

            # Mutate dominating individuals
            mutated_result = self.sample_mutated(parent_languages)
            languages = mutated_result

        # update with final generation
        explored_languages.extend(copy.copy(languages))
        dominating_languages = pareto_optimal_languages(
            languages,
            self.objectives,
            unique=True,
            front_pbar=front_pbar,
        )

        return {
            "dominating_languages": dominating_languages,
            "explored_languages": list(set(explored_languages)),
        }

    def sample_mutated(self, languages: list[Language]) -> list[Language]:
        """
        Arguments:
            languages: dominating languages of a generation

            amount: sample_size.

            expressions: the list of expressions


        Returns:
            list of updated languages
        """
        amount = self.sample_size
        amount -= len(languages)
        amount_per_lang = int(math.floor(amount / len(languages)))
        amount_random = amount % len(languages)

        mutated_languages = []

        for language in languages:
            for _ in range(amount_per_lang):
                num_mutations = random.randint(1, self.max_mutations)

                mutated_language = language

                for _ in range(num_mutations):
                    mutated_language = self.mutate(mutated_language)
                mutated_languages.append(mutated_language)

        # Ensure the number of languages per generation is constant

        for _ in range(amount_random):
            language = random.choice(languages)
            mutated_languages.append(self.mutate(language))

        mutated_languages.extend(languages)

        return list(set(mutated_languages))

    def mutate(self, language: Language) -> Language:
        """Randomly selects a mutation that is allowed to apply and applies it to a language.

        Args:
            language: the Language to mutate

        Returns:
            the mutated Language

        """
        possible_mutations = [
            mutation
            for mutation in self.mutations
            if mutation.precondition(
                language, lang_size=self.lang_size, objectives=self.objectives
            )
        ]
        mutation = random.choice(possible_mutations)
        return mutation.mutate(language, self.expressions)  # TODO: generalize


def sample_parents(
    dominating_languages: set[Language],
    explored_languages: set[Language],
    explore: float,
) -> list[Language]:
    """Use the explore parameter to explore possibly suboptimal areas of the language space.

    Args:
        dominating_languages: a list of the languages with current best fitness with respect to the objectives.

        explored_languages: a list of all languages encountered during the evolutionary algorithm.

        explore: a float in `[0,1]` specifying how much to explore possibly suboptimal languages.
            If set to 0, `parent_languages` is just `dominating_languages`.

    Returns:
        the languages to serve as the next generation (after possible mutations)
    """
    total_fit = len(dominating_languages)
    num_explore = int(explore * total_fit)
    num_fit = total_fit - num_explore

    parent_languages = random.sample(dominating_languages, num_fit)
    parent_languages.extend(random.sample(explored_languages, num_explore))

    return list(set(parent_languages))
