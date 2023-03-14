from ..meaning import universe as indefinites_universe
from ..measures import comm_cost, complexity
from ..util import read_expressions, read_natural_languages, write_languages

if __name__ == "__main__":
    natural_languages = read_natural_languages(
        "indefinites/data/natural_language_indefinites.csv"
    )
    _, expressions_by_meaning = read_expressions(
        "indefinites/outputs/generated_expressions.yml", universe=indefinites_universe
    )
    # Verify that all NL meanings have been generated by the grammar, so that we can
    # in fact use description length to measure complexity
    assert all(
        expression.meaning in expressions_by_meaning
        for language in natural_languages
        for expression in language.expressions
    )

    write_languages(
        natural_languages,
        "indefinites/outputs/natural_languages.yml",
        {
            "name": lambda _, lang: lang.name,
            "type": lambda _1, _2: "natural",
            "lot_expressions": lambda _, lang: [
                str(expressions_by_meaning[expr.meaning]) for expr in lang.expressions
            ],
            "complexity": lambda _, lang: complexity(lang, expressions_by_meaning),
            "comm_cost": lambda _, lang: comm_cost(lang),
        },
    )
