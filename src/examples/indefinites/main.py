import pandas as pd
from altk.language.language import Language
from altk.language.sampling import all_expressions, all_languages, all_meanings, generate_languages, random_languages

from grammar import indefinites_grammar
from meaning import universe as indefinites_universe


if __name__ == "__main__":

    print(indefinites_universe)

    """
    for exp in indefinites_grammar.enumerate(3):
        print(exp)
        print(exp.to_meaning(indefinites_universe))
    """

    expressions = list(all_expressions(all_meanings(indefinites_universe)))
    for exp in expressions:
        print(exp)

    languages = generate_languages(Language, expressions, 10, 1000)["languages"]
    print(len(languages))
    print([len(language) for language in languages])

    languages = list(all_languages(Language, expressions, 3))
    print(len(languages))

    languages = list(random_languages(Language, expressions, 1000, 7))
    print(len(languages))
    print([len(language) for language in languages])