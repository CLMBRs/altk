from altk.language.grammar import Grammar, GrammaticalExpression, Rule
from altk.language.semantics import Meaning, Referent, Universe

class TestGrammar:

    referents = [Referent(str(num), {'num': num}) for num in range(5)]
    universe = Universe(referents)

    grammar = Grammar(bool)
    grammar.add_rule(Rule(">", bool, (int, int), lambda x, y: x > y))
    grammar.add_rule(Rule("n", int, (), lambda model: model.num))
    for num in range(5):
        grammar.add_rule(Rule(f"{num}", int, (), lambda *args: num))

    geq2_expr_str = ">(n, 2)"

    def test_parse(self):
        parsed_expression = TestGrammar.grammar.parse(TestGrammar.geq2_expr_str)
        assert str(parsed_expression) == TestGrammar.geq2_expr_str
