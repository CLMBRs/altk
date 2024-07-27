from ultk.util.io import write_expressions

from ultk.language.semantics import Meaning
from ultk.language.grammar import Grammar, GrammaticalExpression
from universe import number_universe

if __name__ == "__main__":

    number_grammar: Grammar = Grammar.from_module("grammar")
    expressions_by_meaning: dict[Meaning, GrammaticalExpression] = (
        number_grammar.get_unique_expressions(
            3,
            unique_key=lambda expr: expr.evaluate(number_universe),
            compare_func=lambda e1, e2: len(e1) < len(e2),
        )
    )

    # filter out the trivial meaning, results in NaNs
    # iterate over keys, since we need to change the dict itself
    for meaning in list(expressions_by_meaning.keys()):
        print(expressions_by_meaning[meaning].term_expression)
        if meaning.is_uniformly_false():
            del expressions_by_meaning[meaning]

    print(f"Generated {len(expressions_by_meaning)} unique expressions.")
    write_expressions(expressions_by_meaning.values(), "generated_expressions.yml")
