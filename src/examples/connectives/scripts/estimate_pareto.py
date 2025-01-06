from ultk.effcomm.optimization import EvolutionaryOptimizer
from ultk.language.sampling import random_languages, all_languages
from ultk.util.io import read_grammatical_expressions, write_languages


from ..grammar import connectives_grammar
from ..meaning import universe as connectives_universe
from ..measures import comm_cost, complexity, commutative_only


if __name__ == "__main__":
    expressions, expressions_by_meaning = read_grammatical_expressions(
        "connectives/outputs/generated_expressions.yml",
        connectives_grammar,
        universe=connectives_universe,
        return_by_meaning=True,
    )

    seed_languages = list(all_languages(expressions))
    print(f"Generated all {len(seed_languages)} languages.")

    def lang_commutative(language):
        return commutative_only(language, connectives_grammar)

    def lang_complexity(language):
        return complexity(language, expressions_by_meaning)

    optimizer = EvolutionaryOptimizer(
        [lang_complexity, comm_cost],
        expressions,
    )
    result = optimizer.fit(seed_languages, front_pbar=True)

    print(f"Writing languages...")

    write_languages(
        result["dominating_languages"],
        "connectives/outputs/dominating_languages.yml",
        {
            "name": lambda idx, _: f"dominating-{idx}",
            "type": lambda _1, _2: "dominant",
            "complexity": lambda _, lang: lang_complexity(lang),
            "comm_cost": lambda _, lang: comm_cost(lang),
            "commutative": lambda _, lang: lang_commutative(lang),
        },
    )
    write_languages(
        result["explored_languages"],
        "connectives/outputs/explored_languages.yml",
        {
            "name": lambda idx, _: f"explored-{idx}",
            "type": lambda _1, _2: "explored",
            "complexity": lambda _, lang: lang_complexity(lang),
            "comm_cost": lambda _, lang: comm_cost(lang),
            "commutative": lambda _, lang: lang_commutative(lang),
        },
    )
