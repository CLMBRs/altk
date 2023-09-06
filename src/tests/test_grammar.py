from itertools import product

from ultk.language.semantics import Meaning, Referent, Universe
from ultk.language.grammar.grammar import Grammar, GrammaticalExpression, Rule
from ultk.language.grammar.boolean import BooleanGrammar, RuleNames
from ultk.language.grammar.complexity import num_atoms
import ultk.language.grammar.complexity as complexity
from ultk.language.semantics import Meaning, Referent, Universe

import numpy as np

class TestGrammar:
    referents = [Referent(str(num), {"num": num}) for num in range(4)]
    universe = Universe(referents)

    grammar = Grammar(bool)
    grammar.add_rule(Rule(">", bool, (int, int), lambda x, y: x > y))
    grammar.add_rule(Rule("+", int, (int, int), lambda x, y: x + y))
    grammar.add_rule(Rule("n", int, (), lambda model: model.num))
    grammar.add_rule(Rule(f"0", int, (), lambda *args: 0))
    grammar.add_rule(Rule(f"1", int, (), lambda *args: 1))
    grammar.add_rule(Rule(f"2", int, (), lambda *args: 2))
    grammar.add_rule(Rule(f"3", int, (), lambda *args: 3))

    geq2_expr_str = ">(n, +(1, 1))"

    def test_parse(self):
        parsed_expression = TestGrammar.grammar.parse(TestGrammar.geq2_expr_str)
        assert str(parsed_expression) == TestGrammar.geq2_expr_str

    def test_meaning(self):
        parsed_expression = TestGrammar.grammar.parse(TestGrammar.geq2_expr_str)
        expr_meaning = parsed_expression.evaluate(TestGrammar.universe)
        goal_meaning = Meaning(
            [referent for referent in TestGrammar.referents if referent.num > 2],
            TestGrammar.universe,
        )
        assert expr_meaning == goal_meaning

    def test_length(self):
        parsed_expression = TestGrammar.grammar.parse(TestGrammar.geq2_expr_str)
        assert len(parsed_expression) == 5

    def test_atoms(self):
        parsed_expression = TestGrammar.grammar.parse(TestGrammar.geq2_expr_str)
        assert num_atoms(parsed_expression) == 3

    def test_yield(self):
        parsed_expression = TestGrammar.grammar.parse(TestGrammar.geq2_expr_str)
        assert parsed_expression.yield_string() == "n11"

    def test_enumerate(self):
        enumed_grammar = TestGrammar.grammar.get_unique_expressions(
            depth=1, lhs=(int, int)
        )
        print("Enumed Grammar Rules with len")
        print(enumed_grammar)
        for rule in enumed_grammar:
            print(rule)


