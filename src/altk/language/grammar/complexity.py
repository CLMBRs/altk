from altk.language.grammar.grammar import GrammaticalExpression


def expression_length(expr: GrammaticalExpression) -> int:
    return len(expr)


def num_atoms(expr: GrammaticalExpression) -> int:
    if expr.children is None:
        return 1
    return sum(num_atoms(child) for child in expr.children)
