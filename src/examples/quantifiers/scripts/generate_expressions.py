from yaml import dump

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from examples.quantifiers.grammar import grammar
from examples.quantifiers.meaning import universe

if __name__ == "__main__":
    expressions_by_meaning = grammar.get_unique_expressions(
        3,
        max_size=2 ** len(universe),
        unique_key=lambda expr: expr.evaluate(universe),
        compare_func=lambda e1, e2: len(e1) < len(e2),
    )

    # filter out the trivial meaning, results in NaNs
    # iterate over keys, since we need to change the dict itself
    for meaning in list(expressions_by_meaning.keys()):
        if len(meaning.referents) == 0:
            del expressions_by_meaning[meaning]

    # TODO: make this file reusable by having the output file location as a parameter
    with open("quantifiers/outputs/generated_expressions.yml", "w") as outfile:
        dump(
            [
                expressions_by_meaning[meaning].to_dict()
                for meaning in expressions_by_meaning
            ],
            outfile,
            Dumper=Dumper,
        )
