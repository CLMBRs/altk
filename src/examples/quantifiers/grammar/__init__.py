from ultk.language.grammar import Grammar
from ultk.language.grammar import Grammar

quantifiers_grammar = Grammar.from_yaml("quantifiers/grammar/grammar.yml")
# quantifiers_grammar = Grammar.from_module("quantifiers.grammar.full")
quantifiers_grammar_natural = Grammar.from_module("quantifiers.grammar.natural")
