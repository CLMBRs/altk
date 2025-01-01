from ultk.util.io import write_expressions
from ultk.language.semantics import Meaning
from ultk.language.grammar import Grammar, GrammaticalExpression

from kinship.meaning import universe as kinship_universe
kinship_grammar = Grammar.from_module("kinship.new_grammar_functions")

if __name__ == "__main__":

    breakpoint()

    expressions_by_meaning: dict[Meaning, GrammaticalExpression] = (
        kinship_grammar.get_unique_expressions(
            5,
            max_size=2 ** len(kinship_universe),
            # max_size=100,
            unique_key=lambda expr: expr.evaluate(kinship_universe),
            compare_func=lambda e1, e2: len(e1) < len(e2),
        )
    )

    # filter out the trivial meaning, results in NaNs
    # iterate over keys, since we need to change the dict itself
    for meaning in list(expressions_by_meaning.keys()):
        if meaning.is_uniformly_false():
            del expressions_by_meaning[meaning]

    print(f"Generated {len(expressions_by_meaning)} unique expressions.")
    print(list((v.term_expression, len(list(x for x in k.mapping if k.mapping[x]))) for k,v in expressions_by_meaning.items()))
    breakpoint()
    results = {e.term_expression: set(x for x in e.meaning if e.meaning[x]) for e in expressions_by_meaning.values()}
    for k,v in results.items():
        print(k)
        print("-------------------------------------------")
        [print(x) for x in v]
        print("-------------------------------------------")        

    write_expressions(
        expressions_by_meaning.values(), "kinship/outputs/generated_expressions.yml"
    )
