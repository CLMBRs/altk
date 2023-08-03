from altk.language.grammar.grammar import GrammaticalExpression


def expression_length(expr: GrammaticalExpression) -> int:
    """Get the expression length (number of nodes in a tree).
    See `GrammaticalExpression.__len__` for more information.

    Args:
        expr: the expression

    Returns:
        the expression's length
    """
    return len(expr)


def num_atoms(expr: GrammaticalExpression) -> int:
    """Count the number of atoms in a GrammaticalExpression.

    Args:
        expr: the expression

    Returns:
        the number of atoms
    """
    if expr.is_atom():
        return 1
    return sum(num_atoms(child) for child in expr.children)


################################################################
# Boolean Operations
################################################################


def distribute_and(expr: GrammaticalExpression) -> GrammaticalExpression:
    """(p and q) or (p and s) -> p and (q or s)"""
    pass
