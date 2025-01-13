import random
from copy import deepcopy
from tqdm import tqdm

from ..grammar import base_numerals_grammar, Grammar, Rule
from ..numerals_language import NumeralsLanguage, Number, Multiplier
from ..meaning import numbers, universe


from functools import partial

def generate_numerals_language() -> NumeralsLanguage:
    # Draw two random samples of numbers between 1 and 99; 
    # these stand for morphemes of category D and M, respectively.

    # First, randomly sample k
    k = random.choice(numbers)
    digits = random.sample(numbers, k)

    k = random.choice(range(5+1))
    multipliers = random.sample(numbers, k)

    grammar = deepcopy(base_numerals_grammar)

    # Add D rules
    for digit in digits:
        # Use partial to capture the value of digit explicitly
        grammar.add_rule(
            Rule(
                f"_{digit}_D", Number, None, func=partial(lambda digit_value, _: digit_value, digit),
            )
        )
        
    # Add M rules
    for multiplier in multipliers:
        # Use partial to capture the value of multiplier explicitly
        grammar.add_rule(
            Rule(
                f"_{multiplier}_M", Multiplier, None, func=partial(lambda multiplier_value, _: multiplier_value, multiplier),
            )
        )
    
    # print(grammar)
    
    language = NumeralsLanguage.from_grammar(grammar)
    return language

def get_good_lang() -> NumeralsLanguage:
    while True:
        new_language = generate_numerals_language()
        if len(new_language.get_names()) >= len(universe):
            return new_language


def sample_numerals_languages(size: int = 2000) -> list[NumeralsLanguage]:
    langs = set()
    pbar = tqdm(total=size, desc="Generating languages", unit="lang")
    while len(langs) < size:
        new_lang = get_good_lang()
        if new_lang not in langs:
            langs.add(new_lang)
            pbar.update(1)  # Update progress bar
    pbar.close()  # Close the progress bar when done
    return list(langs)
