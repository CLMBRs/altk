import random
from altk.language.grammar import Grammar, Rule

from meaning import all_models_up_to_size

if __name__ == '__main__':
    quantifier_grammar = Grammar(bool)
    quantifier_grammar.add_rule(Rule(bool, (bool, bool), lambda b1, b2: b1 and b2, "and"))
    quantifier_grammar.add_rule(Rule(bool, (set, set), lambda s1, s2: s1 <= s2, "subset"))
    quantifier_grammar.add_rule(Rule(set, (), lambda model: model.A, "A"))
    quantifier_grammar.add_rule(Rule(set, (), lambda model: model.B, "B"))
    print(quantifier_grammar)

    expression = quantifier_grammar.generate()
    print(f"Expression: {expression}")

    models = all_models_up_to_size(3)
    test_models = random.choices(list(models.referents), k=3)
    for model in test_models:
        print(f"Model: {model}")
        print(f"Output: {expression(model)}\n")