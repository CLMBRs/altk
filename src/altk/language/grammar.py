import random
from collections import defaultdict
from typing import Any, Callable, Iterable

from altk.language.semantics import Meaning, Referent, Universe


class Rule:
    def __init__(
        self,
        lhs: Any,
        rhs: Iterable[Any],
        func: Callable = lambda *args: None,
        name: str = "",
        weight: float = 1.0,
    ):
        self.lhs = lhs
        self.rhs = rhs
        self.func = func
        self.name = name
        self.weight = weight

    def is_terminal(self) -> bool:
        return len(self.rhs) == 0

    def __str__(self) -> str:
        out_str = f"{str(self.lhs)} -> {self.name}"
        if not self.is_terminal():
            out_str += f"({', '.join(str(typ) for typ in self.rhs)})"
        return out_str


class GrammaticalExpression:
    def __init__(self, name: str, func: Callable, children: Iterable):
        self.name = name
        self.func = func
        self.children = children

    def to_meaning(self, universe: Universe):
        # TODO: this presupposes that the expression has type Referent -> bool.  Should we generalize?
        return Meaning([referent for referent in universe.referents if self(referent)], universe)

    def __call__(self, referent: Referent):
        if len(self.children) == 0:
            return self.func(referent)
        return self.func(*(child(referent) for child in self.children))

    def __str__(self):
        out_str = self.name
        if len(self.children) > 0:
            out_str += f"({', '.join(str(child) for child in self.children)})"
        return out_str


class Grammar:
    def __init__(self, start: Any):
        # _rules: nonterminals -> list of rules
        self._rules = defaultdict(list)
        self._start = start

    def add_rule(self, rule: Rule):
        self._rules[rule.lhs].append(rule)

    def generate(self, lhs: Any = None):
        if lhs is None:
            lhs = self._start
        rules = self._rules[lhs]
        the_rule = random.choices(rules, weights=[rule.weight for rule in rules], k=1)[
            0
        ]
        # if the rule is terminal, rhs will be empty, so no recursive calls to generate will be made in this comprehension
        return GrammaticalExpression(
            the_rule.name,
            the_rule.func,
            [self.generate(child_lhs) for child_lhs in the_rule.rhs],
        )

    def get_all_rules(self):
        rules = []
        for lhs in self._rules:
            rules.extend(self._rules[lhs])
        return rules

    def __str__(self):
        return "Rules:\n" + "\n".join(f"\t{rule}" for rule in self.get_all_rules())
