import random
import numpy as np
from ultk.effcomm.optimization import EvolutionaryOptimizer
from ultk.language.sampling import random_languages, generate_languages, Language
from ultk.util.io import read_grammatical_expressions, write_languages

from ..grammar import quantifiers_grammar
from ..meaning import universe as quantifiers_universe
from ..measures import comm_cost, complexity, quasi_natural


if __name__ == "__main__":
    expressions, expressions_by_meaning = read_grammatical_expressions(
        "quantifiers/outputs/generated_expressions.yml",
        quantifiers_grammar,
        universe=quantifiers_universe,
        return_by_meaning=True,
    )

    random.seed(42)
    np.random.seed(42)
    seed_languages = generate_languages(
        Language,
        expressions,
        10,
        10000,
        quasi_natural,
    )["languages"]

    print(f"Discovered {len(seed_languages)} languages by sampling.")

    def naturalness(language):
        return sum(quasi_natural(e) for e in language.expressions) / len(language)

    def lang_complexity(language):
        return complexity(language, expressions_by_meaning)

    optimizer = EvolutionaryOptimizer(
        [lang_complexity, comm_cost],
        expressions,
        1000,
        3,
        50,
    )
    result = optimizer.fit(seed_languages)

    write_languages(
        result["dominating_languages"],
        "quantifiers/outputs/dominating_languages.yml",
        {
            "name": lambda idx, _: f"dominating-{idx}",
            "type": lambda _1, _2: "dominant",
            "complexity": lambda _, lang: lang_complexity(lang),
            "comm_cost": lambda _, lang: comm_cost(lang),
            "naturalness": lambda _, lang: naturalness(lang),
        },
    )
    write_languages(
        result["explored_languages"],
        "quantifiers/outputs/explored_languages.yml",
        {
            "name": lambda idx, _: f"explored-{idx}",
            "type": lambda _1, _2: "explored",
            "complexity": lambda _, lang: lang_complexity(lang),
            "comm_cost": lambda _, lang: comm_cost(lang),
            "naturalness": lambda _, lang: naturalness(lang),
        },
    )
