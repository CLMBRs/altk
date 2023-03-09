import random
import re
from collections import defaultdict
from itertools import product
from typing import Any, Callable, Generator, Iterable

from altk.language.semantics import Meaning, Referent, Universe


class Rule:
    """Basic class for a grammar rule.  Grammar rules in ALTK correspond
    to functions.  One can think of a grammar as generating complex functions from
    more basic ones.

    Attributes:
        lhs: left-hand side of the rule (can be anything)
            conceptually, the output type of a function
        rhs: right-hand side; assumed to be an iterable
            conceptually, a list of types of inputs
        func: a callable, the function to be computed when a node with this rule is executed
        name: name of the function
        weight: a relative weight to assign to this rule
            when added to a grammar, all rules with the same LHS will be weighted together
    """

    def __init__(
        self,
        name: str,
        lhs: Any,
        rhs: Iterable[Any],
        func: Callable = lambda *args: None,
        weight: float = 1.0,
    ):
        self.lhs = lhs
        self.rhs = rhs
        self.func = func
        self.name = name
        self.weight = weight

    def is_terminal(self) -> bool:
        """Whether this is a terminal rule.  In our framework, this means that RHS is empty,
        i.e. there are no arguments to the function.
        """
        return len(self.rhs) == 0

    def __str__(self) -> str:
        out_str = f"{str(self.lhs)} -> {self.name}"
        if not self.is_terminal():
            out_str += f"({', '.join(str(typ) for typ in self.rhs)})"
        return out_str


class GrammaticalExpression:
    """A GrammaticalExpression has been built up from a Grammar by applying a sequence of Rules.
    Crucially, it is _callable_, using the functions corresponding to each rule.

    A GrammaticalExpression, when called, takes in a Referent.  Because of this, a Meaning can
    be generated by specifying a Universe (which contains Referents).

    Attributes:
        name: name of the top-most function
        func: the function
        children: child expressions (possibly empty)
    """

    def __init__(self, name: str, func: Callable, children: Iterable):
        self.name = name
        self.func = func
        self.children = children

    def to_meaning(self, universe: Universe) -> Meaning:
        # TODO: this presupposes that the expression has type Referent -> bool.  Should we generalize?
        return Meaning(
            [referent for referent in universe.referents if self(referent)], universe
        )

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
    """At its core, a Grammar is a set of Rules with methods for generating GrammaticalExpressions."""

    def __init__(self, start: Any):
        # _rules: nonterminals -> list of rules
        self._rules = defaultdict(list)
        # name -> rule, for fast lookup in parsing
        self._rules_by_name = {}
        self._start = start

    def add_rule(self, rule: Rule):
        self._rules[rule.lhs].append(rule)
        if rule.name in self._rules_by_name:
            raise ValueError(
                f"Rules of a grammar must have unique names. This grammar already has a rule named {name}."
            )
        self._rules_by_name[rule.name] = rule

    def parse(
        self,
        expression: str,
        opener: str = "(",
        closer: str = ")",
        delimiter: str = ",",
    ) -> GrammaticalExpression:
        """Parse a string representation of an expression of a grammar.
        Note that this is not a general-purpose parsing algorithm.  We assume that the strings are of the form
            parent_name(child1_name, ..., childn_name)
        where parent_name is the name of a rule of this grammar that has a length-n RHS, and that
        childi_name is the name of a rule for each child i.

        Args:
            expression: string in the above format

        Returns:
            the corresponding GrammaticalExpression
        """
        # see nltk.tree.Tree.fromstring for inspiration
        # tokenize string roughly by splitting at open brackets, close brackets, and delimiters
        open_re, close_re, delimit_re = (
            re.escape(opener),
            re.escape(closer),
            re.escape(delimiter),
        )
        token_regex = re.compile(
            f"[.]+{open_re}|[^{open_re}{close_re}{delimit_re}]+|{delimit_re}(\s)*|{close_re}"
        )

        # stack to store the tree being built
        stack = []

        for token in token_regex.finditer(expression):
            # strip trailing whitespace if needed
            token = token.group().strip()
            # start a new expression
            if token[-1] == opener:
                name = token[:-1]
                stack.append(GrammaticalExpression(name, self._rules_by_name[name].func, []))
            # finish an expression
            elif token == delimiter or token == closer:
                # finished a child expression
                # TODO: are there edge cases that distinguish delimiter from closer?
                child = stack.pop()
                stack[-1].children.append(child)
            else:
                # primitive, no children, just look up
                stack.append(
                    GrammaticalExpression(token, self._rules_by_name[token].func, [])
                )
        if len(stack) != 1:
            raise ValueError("Could not parse string {expression}")
        return stack[0]

    def generate(self, lhs: Any = None) -> GrammaticalExpression:
        """Generate an expression from a given lhs."""
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

    # TODO: add filtering to enumeration in order to only add GrammaticalExpressions with a unique Meaning? (or any other filter)
    def enumerate(
        self, depth: int = 8, lhs: Any = None
    ) -> Generator[GrammaticalExpression, None, None]:
        """Enumerate all expressions from the grammar up to a given depth from a given LHS.

        Args:
            depth: how deep the trees should be
            lhs: left hand side to start from; defaults to the grammar's start symbol

        Yields:
            all GrammaticalExpressions up to depth
        """
        if lhs is None:
            lhs = self._start
        for num in range(depth):
            for expr in self.enumerate_at_depth(num, lhs):
                yield expr

    def enumerate_at_depth(
        self, depth: int, lhs: Any
    ) -> Generator[GrammaticalExpression, None, None]:
        """Enumerate GrammaticalExpressions for this Grammar _at_ a fixed depth."""
        if depth == 0:
            for rule in self._rules[lhs]:
                if rule.is_terminal():
                    yield GrammaticalExpression(rule.name, rule.func, [])

        for rule in self._rules[lhs]:
            # can't use terminal rules when depth > 0
            if rule.is_terminal():
                continue

            # get lists of possible depths for each child
            for child_depths in product(range(depth), repeat=len(rule.rhs)):
                if max(child_depths) < depth - 1:
                    continue
                # get all possible children of the relevant depths
                children_iter = product(
                    *[
                        self.enumerate_at_depth(child_depth, child_lhs)
                        for child_depth, child_lhs in zip(child_depths, rule.rhs)
                    ]
                )
                for children in children_iter:
                    yield GrammaticalExpression(rule.name, rule.func, children)

    def get_all_rules(self) -> list[Rule]:
        """Get all rules as a list."""
        rules = []
        for lhs in self._rules:
            rules.extend(self._rules[lhs])
        return rules

    def __str__(self):
        return "Rules:\n" + "\n".join(f"\t{rule}" for rule in self.get_all_rules())
