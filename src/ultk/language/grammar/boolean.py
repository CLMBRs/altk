from enum import StrEnum
from typing import Callable
from ultk.language.grammar.grammar import Grammar, GrammaticalExpression, Rule


class RuleNames(StrEnum):
    AND = "and"
    OR = "or"
    NOT = "not"


class BooleanGrammar(Grammar):
    def __init__(self):
        super().__init__(bool)
        self.add_rule(
            Rule(RuleNames.AND, bool, (bool, bool), lambda p1, p2: p1 and p2)
        )
        self.add_rule(Rule(RuleNames.OR, bool, (bool, bool), lambda p1, p2: p1 or p2))
        self.add_rule(Rule(RuleNames.NOT, bool, (bool,), lambda p1: not p1))

    def add_atom(self, name: str, function: Callable) -> None:
        self.add_rule(Rule(name, bool, None, function))

    def __func_from_name(rule_name: RuleNames):
        """
        Utility function for generating the matching function from a RuleName. 
        """
        if rule_name == RuleNames.AND:
            return lambda *args: all(args)
        if rule_name == RuleNames.OR:
            return lambda *args: any(args)
        if rule_name == RuleNames.NOT:
            return lambda arg: not arg #This, unlike the other two functions, assumes an atomic input, rather than a list
    