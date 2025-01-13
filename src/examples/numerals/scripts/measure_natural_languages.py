from ultk.util.io import read_grammatical_expressions
from ..numerals_language import NumeralsLanguage, get_singleton_meaning
from ..grammar import english_numerals_grammar
from ..meaning import universe as numerals_universe
from ..measures import avg_morph_complexity, lexicon_size
from ..util import read_natural_languages, write_languages

if __name__ == "__main__":

    lang = NumeralsLanguage.from_grammar(english_numerals_grammar)
    lang.name = "English"

    write_languages(
        [lang],
        "numerals/outputs/natural_languages.yml",
        {
            "name": lambda _, lang: lang.name,
            "type": lambda _1, _2: "natural",
            "lot_expressions": lambda _, lang: [
                get_singleton_meaning(expr) for expr in lang.expressions
            ],
            "avg_morph_complexity": lambda _, lang: avg_morph_complexity(lang),
            "lexicon_size": lambda _, lang: lexicon_size(lang),
        },
    )
