from ultk.effcomm.optimization import Mutation, random
from ..numerals_language import (
    NumeralsLanguage,
    is_D_rule,
    is_M_rule,
    numerals_universe,
)
from ..grammar.base_grammar import Number, Multiplier
from ultk.language.grammar import Grammar, Rule
from copy import deepcopy

from abc import abstractmethod
from typing import Callable, Any


# Helpers
def remove_rule(
    grammar: Grammar,
    filter: Callable[[Rule], bool],
) -> Grammar:
    all_rules = grammar.get_all_rules()
    rule_to_remove = random.choice([rule for rule in all_rules if filter(rule)])
    new_grammar = Grammar(grammar._start)
    for rule in all_rules:
        if rule.name == rule_to_remove:
            continue
        new_grammar.add_rule(rule)
    return new_grammar


def add_rule(
    grammar: Grammar,
    filter: Callable[[Rule], bool],
    lhs: Any,
    postfix: str,
) -> Grammar:
    # pretty numerals specfic
    used = [rule.func(None) for rule in grammar.get_all_rules() if filter(rule)]

    # Check for duplicates
    if len(used) != len(set(used)):
        print("Duplicates found!")
        breakpoint()

    available_names = list(set(numerals_universe.referent_names) - set(used))
    name_to_add = random.choice(available_names)
    rule_to_add = Rule(
        f"_{name_to_add}_{postfix}",
        lhs,
        None,
        func=lambda _: name_to_add,
    )
    new_grammar = deepcopy(grammar)
    try:
        new_grammar.add_rule(rule_to_add)
        # print(name_to_add)
    except:
        breakpoint()
    return new_grammar


MAX_ATTEMPTS = 10000


class GrammarMutation(Mutation):
    """Add or remove a rule to a NumeralsLanguage's grammar."""

    @staticmethod
    @abstractmethod
    def precondition(language: NumeralsLanguage, **kwargs) -> bool:
        """Whether a mutation is allowed to apply to a NumeralsLanguage."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def mutate(
        language: NumeralsLanguage, grammars: set[Grammar], **kwargs
    ) -> NumeralsLanguage:
        """Mutate the language via the grammar, while trying to not search for shortest expressions for repeat languages."""
        raise NotImplementedError()


class RemoveRule(GrammarMutation):
    @staticmethod
    def mutate(
        language: NumeralsLanguage, grammars: set[Grammar], category: str, **kwargs
    ) -> NumeralsLanguage:
        # Attempt to generate a new grammar within a reasonable limit
        for _ in range(kwargs.get("max_attempts", MAX_ATTEMPTS)):
            new_grammar = remove_rule(
                language.grammar, is_D_rule if category == "D" else is_M_rule
            )
            if new_grammar not in grammars:
                # Create a new language and check the validity of its expressions
                new_language = NumeralsLanguage.from_grammar(new_grammar)
                if len(new_language.get_names()) == len(numerals_universe):
                    return new_language
        # raise ValueError("Failed to generate a valid new grammar within the attempt limit.")
        # breakpoint()
        return language  # search failed, return original


class RemoveDigit(RemoveRule):
    @staticmethod
    def precondition(language: NumeralsLanguage, *args, **kwargs) -> bool:
        # Ensure there is at least one D rule afterwards
        return language.num_D_morphemes > 1

    @staticmethod
    def mutate(
        language: NumeralsLanguage, grammars: set[Grammar], **kwargs
    ) -> NumeralsLanguage:
        # Explicitly call the parent class method
        return RemoveRule.mutate(language, grammars, category="D", **kwargs)


class RemoveMultiplier(RemoveRule):
    @staticmethod
    def precondition(language: NumeralsLanguage, *args, **kwargs) -> bool:
        # Ensure there is at least one M rule afterwards
        return bool(language.num_M_morphemes)

    @staticmethod
    def mutate(
        language: NumeralsLanguage, grammars: set[Grammar], **kwargs
    ) -> NumeralsLanguage:
        # Explicitly call the parent class method
        return RemoveRule.mutate(language, grammars, category="M", **kwargs)


class AddRule(GrammarMutation):
    @staticmethod
    def mutate(
        language: NumeralsLanguage, grammars: set[Grammar], category: str, **kwargs
    ) -> NumeralsLanguage:
        for _ in range(kwargs.get("max_attempts", MAX_ATTEMPTS)):
            args = (
                (is_D_rule, Number, "D")
                if category == "D"
                else (is_M_rule, Multiplier, "M")
            )
            new_grammar = add_rule(language.grammar, *args)
            if new_grammar not in grammars:
                # Create a new language and check the validity of its expressions
                new_language = NumeralsLanguage.from_grammar(new_grammar)
                if len(new_language.get_names()) == len(numerals_universe):
                    return new_language
        # raise ValueError("Failed to generate a valid new grammar within the attempt limit.")
        return language


class AddDigit(AddRule):
    @staticmethod
    def precondition(language: NumeralsLanguage, *args, **kwargs) -> bool:
        # Skip if we have all the digits
        return language.num_D_morphemes < len(numerals_universe)

    @staticmethod
    def mutate(
        language: NumeralsLanguage, grammars: set[Grammar], **kwargs
    ) -> NumeralsLanguage:
        # Explicitly call the parent class method
        return AddRule.mutate(language, grammars, category="D", **kwargs)


class AddMultiplier(AddRule):
    @staticmethod
    def precondition(language: NumeralsLanguage, *args, **kwargs) -> bool:
        # Don't exceed 5 morphemes
        return language.num_M_morphemes < 5

    @staticmethod
    def mutate(
        language: NumeralsLanguage, grammars: set[Grammar], **kwargs
    ) -> NumeralsLanguage:
        # Explicitly call the parent class method
        return AddRule.mutate(language, grammars, category="M", **kwargs)


# TODO: add an interchange mutation
