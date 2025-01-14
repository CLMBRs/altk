from ultk.util.io import write_expressions

from ultk.language.semantics import Meaning
from ultk.language.grammar import GrammaticalExpression
from ..grammar import english_numerals_grammar as numerals_grammar
from ..meaning import universe as numerals_universe
from ..util import extract_integers


def write_data(expressions_by_meaning: dict[Meaning, GrammaticalExpression]) -> None:
    # For inspecting
    fn = "numerals/outputs/expressions_and_extensions.txt"
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

    print(sorted(extract_integers(fn)))
    print(f"Wrote {len(expressions_by_meaning)} expressions to {fn}.")

    # For loading
    fn = "numerals/outputs/generated_expressions.txt"
    results: list[str] = [e.term_expression for e in expressions_by_meaning.values()]
    with open(fn, "w") as f:
        f.writelines(line + "\n" for line in results)


if __name__ == "__main__":

    expressions_by_meaning: dict[Meaning, GrammaticalExpression] = (
        numerals_grammar.get_unique_expressions(
            4,
            max_size=2 ** len(numerals_universe),
            unique_key=lambda expr: expr.evaluate(numerals_universe),
            compare_func=lambda e1, e2: len(e1) < len(e2),
        )
    )

    print(f"Generated {len(expressions_by_meaning)} unique expressions.")
    # breakpoint()

    write_data(expressions_by_meaning)
