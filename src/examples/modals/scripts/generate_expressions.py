from ultk.util.io import write_expressions

from ultk.language.semantics import Meaning
from ultk.language.grammar import GrammaticalExpression
from ..grammar import modals_grammar
from ..meaning import universe as modals_universe

if __name__ == "__main__":
    expressions_by_meaning: dict[Meaning, GrammaticalExpression] = (
        modals_grammar.get_unique_expressions(
            5,
            max_size=2 ** len(modals_universe),
            unique_key=lambda expr: expr.evaluate(modals_universe),
            compare_func=lambda e1, e2: len(e1) < len(e2),
        )
    )

    # filter out the trivial meaning, results in NaNs
    # iterate over keys, since we need to change the dict itself
    for meaning in list(expressions_by_meaning.keys()):
        if meaning.is_uniformly_false():
            del expressions_by_meaning[meaning]

    print(f"Generated {len(expressions_by_meaning)} unique expressions.")
    write_expressions(
        expressions_by_meaning.values(), "modals/outputs/generated_expressions.yml"
    )