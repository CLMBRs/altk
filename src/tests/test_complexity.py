from ultk.language.semantics import Meaning, Referent, Universe

from ultk.language.grammar.grammar import Grammar, GrammaticalExpression, Rule
from ultk.language.grammar.boolean import BooleanGrammar, RuleNames
from ultk.language.grammar.complexity import num_atoms
import ultk.language.grammar.complexity as complexity
from ultk.language.semantics import Meaning, Referent, Universe
import numpy as np

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
        
    def test_simplify(self):
        meaning = Meaning(referents=[Referent("x", properties={"a1":"x", "a2":"a"})], universe=self.universe)
        minimum_lot =  complexity.minimum_lot_description(meaning,  universe=self.universe, minimization_funcs=[])
        print("Minimum LOT:{}".format(minimum_lot))
        assert minimum_lot

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
        
    def test_array_to_dnf(self):
        arr = np.array([[0, 1, 0],[1,0,0],[0,1,1]])
        print(self.universe.axes_from_referents())
        generated_dnf = complexity.array_to_dnf(arr, self.universe, complement=False)
        print(str(generated_dnf))


    def test_x_contains_x(self):
        assert self.ge_x.contains_name("x") == True
    def test_x_contains_y(self):
        assert self.ge_x.contains_name("y") == False
    def test_xy_contains_x(self):
        assert self.ge_xy.contains_name("x") == True
    def test_xy_contains_y(self):
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
