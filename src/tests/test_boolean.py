from ultk.language.semantics import Meaning, Referent, Universe
from ultk.language.grammar.boolean import BooleanGrammar

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

    
