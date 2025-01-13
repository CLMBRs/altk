from ultk.effcomm.optimization import EvolutionaryOptimizer, random
from .mutations import AddDigit, RemoveDigit, AddMultiplier, RemoveMultiplier
from ..numerals_language import NumeralsLanguage

mutations = (
    AddDigit, 
    RemoveDigit,
    AddMultiplier,
    RemoveMultiplier,
)

class NumeralsOptimizer(EvolutionaryOptimizer):
    """Simple variation on the standard evolutionary algorithm to mutate grammars."""

    def __init__(self, objectives, sample_size = 0, max_mutations = 0, generations = 0, lang_size = None, mutations = mutations):
        super().__init__(objectives, None, sample_size, max_mutations, generations, lang_size, mutations)
        self.grammars = set()

    def mutate(self, language: NumeralsLanguage) -> NumeralsLanguage:
        """Randomly selects a mutation that is allowed to apply and applies it to a language.

        Args:
            language: the NumeralsLanguage to mutate

        Returns:
            the mutated NumeralsLanguage

        """
        possible_mutations = [
            mutation
            for mutation in self.mutations
            if mutation.precondition(language)
        ]
        mutation = random.choice(possible_mutations)
        new_language = mutation.mutate(language, self.grammars,)
        self.grammars.add(new_language.grammar)
        print("Mutation successful")
        return new_language