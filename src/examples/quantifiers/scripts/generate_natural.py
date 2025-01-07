"""Generate attested expressions."""

import re
from ultk.util.io import write_expressions
from ultk.language.semantics import Meaning
from ultk.language.grammar import GrammaticalExpression
from ..grammar import quantifiers_grammar_natural
from ..meaning import universe as quantifiers_universe

def remove_class_cruft(input_string):
    return re.sub(r"<class '([^']+)'>", r"\1", input_string)

if __name__ == "__main__":

    expressions_by_meaning: dict[Meaning, GrammaticalExpression] = (
        quantifiers_grammar_natural.get_unique_expressions(
            4, # 8 is too high
            max_size=2 ** len(quantifiers_universe),
            unique_key=lambda expr: expr.evaluate(quantifiers_universe),
            compare_func=lambda e1, e2: len(e1) < len(e2),
        )
    )

    print(f"Generated {len(expressions_by_meaning)} unique expressions.")
    write_expressions(
        expressions_by_meaning.values(), "quantifiers/outputs/natural_generated_expressions.yml"
    )

    with open("quantifiers/outputs/natural_expressions_and_extensions.txt", "w") as f:
        for meaning in expressions_by_meaning.keys():
            f.write("------------------------------------------\n")
            f.write(f"{expressions_by_meaning[meaning].term_expression}\n")
            f.write(f"length = {expressions_by_meaning[meaning].__len__()}\n")
            f.write("------------------------------------------\n")
            set_representation = {m.name for m in meaning if meaning[m]}
            f.writelines(f"{item}\n" for item in set_representation)

    with open("quantifiers/outputs/grammar_rules.txt", "w") as f:
        f.write(remove_class_cruft(str(quantifiers_grammar_natural)))
