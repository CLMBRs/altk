from ..evolution.optimization import NumeralsOptimizer
from ..evolution.sampling import sample_numerals_languages
from ..measures import avg_morph_complexity, lexicon_size
from ..util import write_languages
from ..meaning import universe

if __name__ == "__main__":

    seed_languages = sample_numerals_languages(
        200,
    )

    optimizer = NumeralsOptimizer(
        objectives=[avg_morph_complexity, lexicon_size],
        sample_size=200,
        max_mutations=3,
        generations=50,
        lang_size=len(universe),
    )
    result = optimizer.fit(seed_languages)

    write_languages(
        result["dominating_languages"],
        "numerals/outputs/dominating_languages.yml",
        {
            "name": lambda idx, _: f"dominating-{idx}",
            "type": lambda _1, _2: "dominant",
            "avg_morph_complexity": lambda _, lang: avg_morph_complexity(lang),
            "lexicon_size": lambda _, lang: lexicon_size(lang),
        },
    )
    write_languages(
        result["explored_languages"],
        "numerals/outputs/explored_languages.yml",
        {
            "name": lambda idx, _: f"explored-{idx}",
            "type": lambda _1, _2: "explored",
            "avg_morph_complexity": lambda _, lang: avg_morph_complexity(lang),
            "lexicon_size": lambda _, lang: lexicon_size(lang),
        },
    )
