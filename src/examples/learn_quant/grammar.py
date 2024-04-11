from ultk.language.grammar import Grammar, Rule

class QuantifierGrammar(Grammar):
    """This is a grammar class but for experiments involving quantifiers.

    The class contains functions to dynamically generate rules for the grammar, such as providing it with a variable or defined number of integer primitives.

    Args:
        Grammar (Grammar): The grammar class to inherit from.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any additional initialization code here

    from typing import Union, List

    def add_index_primitive(self, index: int, weight: float):
        """Add an index as a primitive to the grammar.

        Args:
            index (int): Index to add as a primitive.
            weight (float): Weight of the rule.
        """
        self.add_rule(Rule(name="{}".format(index),
                           lhs="int",
                           rhs=None,
                           func=lambda _: index,
                           weight=weight))

    def add_indices_as_primitives(self, indices: Union[int, List[int]], weight: float = 2.0) -> Grammar:
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

quantifiers_grammar = QuantifierGrammar.from_yaml("learn_quant/grammar.yml")