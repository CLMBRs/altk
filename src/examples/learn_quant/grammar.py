from ultk.language.grammar import Grammar, Rule
from typing import Iterable


class QuantifierGrammar(Grammar):
    """This is a grammar class but for experiments involving quantifiers.

    The class contains functions to dynamically generate rules for the grammar, such as providing it with a variable or defined number of integer primitives.

    Args:
        Grammar (Grammar): The grammar class to inherit from.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any additional initialization code here

    def __or__(self, other: "QuantifierGrammar") -> "QuantifierGrammar":
        # Combine two grammars into one, with the same start symbol.
        if self._start != other._start:
            raise ValueError(
                "QuantifierGrammar must have the same start symbol to be combined."
            )
        new_grammar = QuantifierGrammar(self._start)
        for rule in self.get_all_rules() + other.get_all_rules():
            new_grammar.add_rule(rule)
        return new_grammar

    def add_index_primitive(self, index: int, weight: float):
        """Add an index as a primitive to the grammar.

        Args:
            index (int): Index to add as a primitive.
            weight (float): Weight of the rule.
        """
        self.add_rule(
            Rule(
                name="{}".format(index),
                lhs="int",
                rhs=None,
                func=lambda _: index,
                weight=weight,
            )
        )

    def add_indices_as_primitives(
        self, indices: int | list[int], weight: float = 2.0
    ) -> Grammar:
        """Add indices as primitives to the grammar.

        Args:
            indices (int or list[int]): If an `int`, defines the range (max) of indices until which to create primitive rules.
                                        If a `list[int]`, defines specific indices to add as primitives.

        Returns:
            Grammar: The grammar with the indices as primitives.
        """

        if isinstance(indices, int):
            for index in range(indices):
                self.add_index_primitive(index, weight)
        elif isinstance(indices, list):
            for index in indices:
                self.add_index_primitive(index, weight)


def get_indices_tag(indices=True) -> str:

    if indices is True:
        indices_tag = ""
    elif indices is False:
        indices_tag = "_xidx"
    elif isinstance(indices, int):
        indices_tag = f"_E{indices}"
    elif isinstance(indices, Iterable):
        indices_tag = "_" + "-".join([str(x) for x in list(indices)])
    else:
        raise ValueError("Invalid type for indices. Must be bool, int, or iterable.")

    return indices_tag


def add_indices(
    grammar: QuantifierGrammar, m_size: int, weight: int, indices=True
) -> QuantifierGrammar:

    indices_tag = get_indices_tag(indices)

    if indices is True:
        print("Adding all indices up to m_size")
        grammar.add_indices_as_primitives(m_size, weight)
    elif isinstance(indices, int):
        if not isinstance(indices, bool):
            indices = list(range(0, m_size, indices))
            grammar.add_indices_as_primitives(indices, weight)
    elif isinstance(indices, Iterable):
        grammar.add_indices_as_primitives(list(indices), weight)
    else:
        raise ValueError("Invalid type for indices. Must be bool, int, or iterable.")

    return grammar, indices_tag


quantifiers_grammar = QuantifierGrammar.from_yaml("learn_quant/grammar.yml")
quantifiers_grammar_xprimitives = QuantifierGrammar.from_yaml(
    "learn_quant/grammar_xprimitives.yml"
)
