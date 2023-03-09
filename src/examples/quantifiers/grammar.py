import random
import re
from altk.language.grammar import Grammar, Rule

from meaning import all_models_up_to_size

if __name__ == '__main__':
    quantifier_grammar = Grammar(bool)
    quantifier_grammar.add_rule(Rule("and", bool, (bool, bool), lambda b1, b2: b1 and b2))
    quantifier_grammar.add_rule(Rule("subset", bool, (set, set), lambda s1, s2: s1 <= s2))
    quantifier_grammar.add_rule(Rule("A", set, (), lambda model: model.A))
    quantifier_grammar.add_rule(Rule("B", set, (), lambda model: model.B))
    print(quantifier_grammar)

    expression = quantifier_grammar.generate()
    print(f"Expression: {expression}")

    models = all_models_up_to_size(3)
    test_models = random.choices(list(models.referents), k=3)
    for model in test_models:
        print(f"Model: {model}")
        print(f"Output: {expression(model)}\n")
    meaning = expression.to_meaning(models)
    print(meaning.referents)

    for expr in quantifier_grammar.enumerate_at_depth(3, bool):
        print(expr)

    expr1 = "subset(B, B)"
    expr2 = "and(subset(A, B), subset(B, B))"

    expr_re = re.compile("[a-z]+\(|[^\(\),]+|,(\s)*|\)")
    for token in expr_re.finditer(expr1):
        print(token.group())
    for token in expr_re.finditer(expr2):
        print(token.group())

    print(quantifier_grammar.parse(expr1))
    print(quantifier_grammar.parse(expr2))