from ultk.util.io import write_expressions
from ultk.language.semantics import Meaning
from ultk.language.grammar import Grammar, GrammaticalExpression

from kinship.meaning import universe as kinship_universe
from kinship.grammar import kinship_grammar


def write_data(expressions_by_meaning: dict[Meaning, GrammaticalExpression]) -> None:
    # For inspecting
    fn = "kinship/outputs/expressions_and_extensions.txt"
    results = {
        e.term_expression: set(x for x in e.meaning if e.meaning[x])
        for e in expressions_by_meaning.values()
    }
    with open(fn, "w") as f:
        for k, v in results.items():
            f.write(k + "\n")
            f.write("-------------------------------------------\n")
            for x in v:
                f.write(str(x.name) + "\n")
            f.write("-------------------------------------------\n")

    print(f"Wrote {len(expressions_by_meaning)} expressions to {fn}.")

    # For loading
    fn = "kinship/outputs/generated_expressions.txt"
    results: list[str] = [e.term_expression for e in expressions_by_meaning.values()]
    with open(fn, "w") as f:
        f.writelines(line + "\n" for line in results)


if __name__ == "__main__":
    expressions_by_meaning: dict[
        Meaning, GrammaticalExpression
    ] = kinship_grammar.get_unique_expressions(
        5,  # I found 6 is too high
        max_size=2 ** len(kinship_universe),
        # max_size=100,
        unique_key=lambda expr: expr.evaluate(kinship_universe),
        compare_func=lambda e1, e2: len(e1) < len(e2),
    )

    # filter out the trivial meaning, results in NaNs
    # iterate over keys, since we need to change the dict itself
    for meaning in list(expressions_by_meaning.keys()):
        if meaning.is_uniformly_false():
            del expressions_by_meaning[meaning]

    write_data(expressions_by_meaning)
