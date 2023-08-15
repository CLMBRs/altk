from ultk.language.semantics import Meaning, Referent, Universe

from ultk.language.grammar.grammar import Grammar, GrammaticalExpression, Rule
from ultk.language.grammar.boolean import BooleanGrammar, RuleNames
from ultk.language.grammar.complexity import num_atoms
import ultk.language.grammar.complexity as complexity
from ultk.language.semantics import Meaning, Referent, Universe


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

class TestComplexity:
    ge_x = GrammaticalExpression(rule_name="x",children=None)
    ge_y = GrammaticalExpression(rule_name="y",children=None)
    ge_z = GrammaticalExpression(rule_name="z",children=None)

    ge_0 = GrammaticalExpression(rule_name="0",children=None)
    ge_1 = GrammaticalExpression(rule_name="1",children=None)

    ge_xy = GrammaticalExpression(rule_name=RuleNames.AND, children=[ge_x, ge_y])
    ge_xz = GrammaticalExpression(rule_name=RuleNames.AND, children=[ge_x, ge_z])

    undistr_expr = GrammaticalExpression(RuleNames.OR, children=[ge_xy, ge_xz] )
    distr_expr = GrammaticalExpression(RuleNames.AND, children=[ge_x, GrammaticalExpression(RuleNames.OR, children=[ge_y, ge_z])])
    
    def test_distribute_and_over_or(self):
        result = complexity.distribute_and_over_or(self.undistr_expr)
        assert result == self.distr_expr

    def test_negation(self):
        result = complexity.negation(self.ge_x)
        assert result == GrammaticalExpression(RuleNames.NOT, children=[self.ge_x])

    def test_coverage(self):
        return NotImplementedError
    
    def test_complement(self):
        return NotImplementedError
    
    def test_or_identity(self):
        return NotImplementedError
    
    def test_and_identity(self):
        assert complexity.identity_and(GrammaticalExpression(RuleNames.AND, children=[self.ge_x, self.ge_y, self.ge_0, self.ge_z])) == GrammaticalExpression(RuleNames.AND, children=[self.ge_x, self.ge_y, self.ge_z])
        assert complexity.identity_and(GrammaticalExpression(RuleNames.AND, children=[self.ge_x, self.ge_0])) == self.ge_x
        assert complexity.identity_and(GrammaticalExpression(RuleNames.AND, children=[self.ge_0])) == self.ge_0

class TestBoolean:
    referents = [
        Referent(f"p1-{p1}_p2-{p2}", {"p1": p1, "p2": p2})
        for p1 in range(3)
        for p2 in range(2)
    ]
    universe = Universe(referents)
    grammar = BooleanGrammar()
    grammar.add_atom("p1-0", lambda point: point.p1 == 0)
    grammar.add_atom("p1-1", lambda point: point.p1 == 1)
    grammar.add_atom("p1-2", lambda point: point.p1 == 2)
    grammar.add_atom("p2-0", lambda point: point.p2 == 0)
    grammar.add_atom("p2-1", lambda point: point.p2 == 1)

    test_expr = "and(p1-0, p2-1)"

    def test_meaning(self):
        parsed_expression = TestBoolean.grammar.parse(TestBoolean.test_expr)
        expr_meaning = parsed_expression.evaluate(TestBoolean.universe)
        goal_meaning = Meaning(
            [ref for ref in TestBoolean.referents if ref.p1 == 0 and ref.p2 == 1],
            TestBoolean.universe,
        )
        assert expr_meaning == goal_meaning

    
