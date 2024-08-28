from ultk.util.io import read_grammatical_expressions

from ultk.language.grammar import Grammar, GrammaticalExpression


if __name__ == "__main__":
    number_grammar: Grammar = Grammar.from_module("grammar")
    # generated_expressions: list[GrammaticalExpression]
    generated_expressions, expressions_by_meaning = read_grammatical_expressions(
        "generated_expressions.yml",
        number_grammar,
    )

    print([expression.term_expression for expression in generated_expressions])
    print(generated_expressions[0].meaning)

    # more stuff here :)
