from .grammar import english_numerals_grammar
from .grammar.base_grammar import Number, Multiplier
from .meaning import universe as numerals_universe
from ultk.language.grammar import Grammar, GrammaticalExpression, Rule
from ultk.language.language import Language, Meaning

from typing import Callable


def get_singleton_meaning(expr: GrammaticalExpression) -> int:
    return [m.name for m in expr.meaning if expr.meaning[m]][0]


def is_D_rule(rule: Rule) -> bool:
    return rule.lhs == Number and rule.rhs is None


def is_M_rule(rule: Rule) -> bool:
    return rule.lhs == Multiplier


# This is like aggregate_complexity
def count_category_rules(grammar: Grammar, func: Callable[[Rule], bool]) -> int:
    return sum(1 for x in grammar._rules_by_name.values() if func(x))


class NumeralsLanguage(Language):
    """Wrapper around Language that can be initialized with a grammar."""

    @classmethod
    def from_grammar(cls, grammar: Grammar, depth: int = 4) -> "NumeralsLanguage":

        # print("Searching for expressions for grammar")
        # print(grammar)
        # print()

        expressions_by_meaning: dict[Meaning, GrammaticalExpression] = (
            grammar.get_unique_expressions(
                depth,
                max_size=2 ** len(numerals_universe),
                unique_key=lambda expr: expr.evaluate(numerals_universe),
                compare_func=lambda e1, e2: len(e1) < len(e2),
            )
        )

        # filter out the trivial meaning, results in NaNs
        # iterate over keys, since we need to change the dict itself
        for meaning in list(expressions_by_meaning.keys()):
            if meaning.is_uniformly_false():
                del expressions_by_meaning[meaning]

        expressions = tuple(expressions_by_meaning.values())
        num_D_rules = count_category_rules(grammar, is_D_rule)
        num_M_rules = count_category_rules(grammar, is_M_rule)
        return cls(
            expressions,
            num_D_morphemes=num_D_rules,
            num_M_morphemes=num_M_rules,
            grammar=grammar,
        )

    def get_names(self) -> set[int]:
        # make sure we can cover the entire universe. In the exact+recursive system, this amounts to whether the system is perfectly informative.
        return {
            m.name for expr in self.expressions for m in expr.meaning if expr.meaning[m]
        }


if __name__ == "__main__":
    # test
    lang = NumeralsLanguage.from_grammar(english_numerals_grammar)
    print(lang.num_D_morphemes)
    print(lang.num_M_morphemes)
