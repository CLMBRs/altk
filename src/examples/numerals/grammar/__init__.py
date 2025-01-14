from ultk.language.grammar import Grammar, Rule
from .base_grammar import Number, Digit, Phrase

english_numerals_grammar = Grammar.from_module("numerals.grammar.english")
base_numerals_grammar = Grammar.from_module("numerals.grammar.base_grammar")
