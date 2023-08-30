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
    referents = [Referent(str(val), {"a1": val}) for val in ["x","y","z"]]
    referents.extend([Referent(str(val), {"a2": val}) for val in ["a","b","c"]])
    referents.append(Referent("0"))
    referents.append(Referent("1"))

    universe = Universe(referents)

    true_meaning = Meaning(referents=referents[0:1], universe=universe)


    ge_x = GrammaticalExpression(rule_name="x", func= lambda *args: "x", children=None)
    ge_y = GrammaticalExpression(rule_name="y", func= lambda *args: "y", children=None)
    ge_z = GrammaticalExpression(rule_name="z", func= lambda *args: "z", children=None)

    ge_a = GrammaticalExpression(rule_name="a", func= lambda *args: "a", children=None)
    ge_b = GrammaticalExpression(rule_name="b", func= lambda *args: "b", children=None)
    ge_c = GrammaticalExpression(rule_name="c", func= lambda *args: "c", children=None)

    ge_0 = GrammaticalExpression(rule_name="0", func= lambda *args: False, children=None)
    ge_1 = GrammaticalExpression(rule_name="1", func= lambda *args: True, children=None)

    ge_xy = GrammaticalExpression(rule_name=RuleNames.AND, func = lambda *args: all(args), children=[ge_x, ge_y])
    ge_xz = GrammaticalExpression(rule_name=RuleNames.AND, func = lambda *args: all(args), children=[ge_x, ge_z])
    ge_a1 = GrammaticalExpression(rule_name=RuleNames.OR, func = lambda *args: any(args), children=[ge_x, ge_y, ge_z])
    ge_a2 = GrammaticalExpression(rule_name=RuleNames.OR, func = lambda *args: any(args), children=[ge_a, ge_b, ge_c])

    undistr_expr = GrammaticalExpression(RuleNames.OR, func = lambda *args: any(args), children=[ge_xy, ge_xz] )
    distr_expr = GrammaticalExpression(RuleNames.AND, func = lambda *args: all(args), children=[ge_x, GrammaticalExpression(RuleNames.OR, lambda *args: any(args), children=[ge_y, ge_z])])
    
    def test_distribute_and_over_or(self):
        result = complexity.distr_or_over_and(self.undistr_expr, self.ge_x)
        assert str(result) == str(self.distr_expr)

    def test_negation(self):
        identity_result = complexity.negation(self.ge_x)
        standard = GrammaticalExpression(RuleNames.NOT, lambda x: not x, children=[self.ge_x])
        print(str(identity_result))
        print(str(standard))
        assert str(identity_result) == str(standard)

    def test_a1_coverage(self):
        axes = self.universe.axes_from_referents()
        #Axes cover all
        assert str(complexity.boolean_cover(self.ge_a1, axes["a1"])) == str(self.ge_1)

    def test_a2_coverage(self):
        axes = self.universe.axes_from_referents()
        #Axes cover all
        assert str(complexity.boolean_cover(self.ge_a2, axes["a2"])) == str(self.ge_1)
    
    def test_a2_not_coverage(self):
        axes = self.universe.axes_from_referents()
        #Axes do not cover 
        assert str(complexity.boolean_cover(self.ge_a2, axes["a1"])) != str(self.ge_1)

    def test_evaluation(self):
        assert self.ge_1.evaluate(self.universe)
        assert not self.ge_0.evaluate(self.universe)

        assert GrammaticalExpression(RuleNames.OR, func=lambda *args: any(args), 
                                     children=[
                                         GrammaticalExpression(RuleNames.AND, func=lambda *args: all(args), children=[self.ge_0, self.ge_1]),
                                         GrammaticalExpression(RuleNames.OR, func=lambda *args: any(args), children=[self.ge_0, self.ge_1])
                                         ]).evaluate(self.universe)
        
        assert not GrammaticalExpression(RuleNames.OR, func=lambda *args: any(args), 
                                children=[
                                    GrammaticalExpression(RuleNames.AND, func=lambda *args: all(args), children=[self.ge_0, self.ge_1]),
                                    GrammaticalExpression(RuleNames.OR, func=lambda *args: any(args), children=[self.ge_0, self.ge_0])
                                    ]).evaluate(self.universe)
        


    def test_complement(self):
        # y or z or (x and z) => ((not x) and (x and z))
        #(+ y z (* a b )) => (+ (- x) (* a b))
        #assert GrammaticalExpression(rule_name=RuleNames.AND, func)
        expr = GrammaticalExpression(rule_name=RuleNames.OR, 
                                        func=lambda *args: any(args),
                                        children=[self.ge_y, self.ge_z, 
                                                  GrammaticalExpression(rule_name=RuleNames.AND, func=lambda *args:all(args), children=[self.ge_a, self.ge_b])])
        intended_expr_result = GrammaticalExpression(rule_name=RuleNames.OR, 
                                        func=lambda *args: any(args),
                                        children=[GrammaticalExpression(rule_name=RuleNames.NOT, func=lambda x: not x, children=[self.ge_x]),
                                                  GrammaticalExpression(rule_name=RuleNames.AND, func=lambda *args:all(args), children=[self.ge_a, self.ge_b])])
        complement = complexity.sum_complement(expr, uni=self.universe)
        #print("Original expr:{}".format(expr))
        #print("Complement expr:{}".format(complement))
        assert str(complement) < str(intended_expr_result)
        

    def test_x_contains_x(self):
        assert self.ge_x.contains_name("x") == True
    def test_x_contains_y(self):
        assert self.ge_x.contains_name("y") == False
    def test_xy_contains_x(self):
        assert self.ge_xy.contains_name("x") == True
    def test_xy_contains_x(self):
        assert self.ge_xy.contains_name("y") == True
    def test_xy_contains_z(self):
        assert self.ge_xy.contains_name("z") == False
    def test_xy_contains_0(self):
        assert self.ge_xy.contains_name("0") == False

    def test_and_identity(self):
        """
        Test the multiplicative identity law.
        """
        #(* a b ... 1 ... c) => (* a b c)
        identity_result = complexity.identity_and(GrammaticalExpression(RuleNames.AND, func = lambda *args: all(args), children=[self.ge_x, self.ge_y, self.ge_1, self.ge_z]))
        standard = GrammaticalExpression(RuleNames.AND, func= lambda *args: any(args), children=[self.ge_x, self.ge_y, self.ge_z])
        print(str(identity_result))
        print(str(standard))
        assert str(identity_result) == str(standard)
        #(* a 1) => (a)
        identity_result = complexity.identity_and(GrammaticalExpression(RuleNames.AND, func = lambda *args: any(args), children=[self.ge_x, self.ge_1])) 
        standard = self.ge_x
        print(str(identity_result))
        print(str(standard))
        assert str(identity_result) == str(standard)

    
    def test_or_identity(self):
        """
        Test the additive identity law.
        """
        #(+ a b ... 0 ... c) => (+ a b c)
        identity_result = complexity.identity_or(GrammaticalExpression(RuleNames.OR, func = lambda *args: any(args), children=[self.ge_x, self.ge_y, self.ge_0, self.ge_z]))
        standard = GrammaticalExpression(RuleNames.OR, func = lambda *args: any(args), children=[self.ge_x, self.ge_y, self.ge_z])
        print(str(identity_result))
        print(str(standard))
        assert str(identity_result) == str(standard)

        #(+ 0) => (0)
        identity_result = complexity.identity_or(GrammaticalExpression(RuleNames.OR, func = lambda *args: any(args), children=[self.ge_0]))
        standard = self.ge_0
        print(str(identity_result))
        print(str(standard))
        assert str(identity_result) == str(standard)
        
        #(+ a 0) => (a)
        identity_result = complexity.identity_or(GrammaticalExpression(RuleNames.OR, func = lambda *args: any(args), children=[self.ge_x, self.ge_0]))
        standard = self.ge_x
        print(str(identity_result))
        print(str(standard))
        assert str(identity_result) == str(standard)

    def test_simplify(self):
        pass
        #simplify_result = complexity.minimum_lot_description()
        


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

    
