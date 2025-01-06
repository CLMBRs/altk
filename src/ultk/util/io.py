import pickle
from ultk.language.language import Expression, Language
from ultk.language.semantics import Meaning, Universe
from ultk.language.grammar import Grammar, GrammaticalExpression
from typing import Iterable, Callable, Any
from yaml import dump, Dumper, load, Loader


def write_expressions(expressions: Iterable[Expression], filename: str) -> None:
    """Write expressions to a YAML file.

    This is particularly useful for writing GrammaticalExpressions, which have a `func` field that can't be serialized. This function uses `to_dict` to determine which properties of the Expression to write.

    Args:
        expressions: the expressions to write
        filename: the file to write to
    """
    with open(filename, "w") as f:
        dump([expr.to_dict() for expr in expressions], f, Dumper=Dumper)


def read_grammatical_expressions(
    filename: str,
    grammar: Grammar,
    re_parse: bool = False,
    universe: Universe | None = None,
    return_by_meaning=True,
) -> tuple[list[GrammaticalExpression], dict[Meaning, GrammaticalExpression]]:
    """Read grammatical expressions from a file, inferring the format from the extension.

    Args:
        filename: the file to read (.yaml or .txt)
        grammar: the grammar to use for parsing
        re_parse: whether to re-parse the expressions (for YAML files)
        universe: the universe to use for evaluation
        return_by_meaning: whether to return a dictionary mapping meanings to expressions or not

    Returns:
        a list of GrammaticalExpressions and a dictionary mapping meanings to expressions
        (empty if `return_by_meaning` is False)
    """
    if filename.endswith(".yaml") or filename.endswith(".yml"):
        return read_grammatical_expressions_from_yaml(
            filename,
            grammar,
            re_parse=re_parse,
            universe=universe,
            return_by_meaning=return_by_meaning,
        )
    elif filename.endswith(".txt"):
        return read_grammatical_expressions_from_txt(
            filename,
            grammar,
            universe=universe,
            return_by_meaning=return_by_meaning,
        )
    else:
        raise ValueError(f"Unsupported file format: {filename}. Must be .yaml or .txt.")


def read_grammatical_expressions_from_yaml(
    filename: str,
    grammar: Grammar,
    re_parse: bool = False,
    universe: Universe | None = None,
    return_by_meaning=True,
) -> tuple[list[GrammaticalExpression], dict[Meaning, GrammaticalExpression]]:
    """Read grammatical expressions from a YAML file.

    Optionally re-parse and (re-)evaluate the expressions using the provided grammar and universe.

    Args:
        filename: the file to read
        grammar: the grammar to use for parsing (and for re-populating the `.func` attribute of each GrammaticalExpression)
        re_parse: whether to re-parse the expressions
        universe: the universe to use for evaluation
        return_by_meaning: whether to return a dictionary mapping meanings to expressions or not

    Returns:
        a list of GrammaticalExpressions and a dictionary mapping meanings to expressions (empty if `return_by_meaning` is False)
    """
    if re_parse and (grammar is None or universe is None):
        raise ValueError("Must provide grammar and universe if re-parsing expressions.")

    with open(filename, "r") as f:
        expression_list = load(f, Loader=Loader)

    if re_parse:
        final_exprs = [
            (
                grammar.parse(expr_dict["term_expression"])
                if re_parse
                else GrammaticalExpression(**expr_dict)
            )
            for expr_dict in expression_list
        ]
    else:
        final_exprs = [
            GrammaticalExpression.from_dict(expr_dict, grammar)
            for expr_dict in expression_list
        ]
    if universe is not None:
        [expr.evaluate(universe) for expr in final_exprs]
    by_meaning = {}
    if return_by_meaning:
        by_meaning = {expr.meaning: expr for expr in final_exprs}
    return final_exprs, by_meaning


def read_grammatical_expressions_from_txt(
    filename: str,
    grammar: Grammar,
    universe: Universe | None = None,
    return_by_meaning=True,
) -> tuple[list[GrammaticalExpression], dict[Meaning, GrammaticalExpression]]:
    """Read grammatical expressions from a text file and re-parse them.

    Args:
        filename: the text file to read (one term_expression per line)
        grammar: the grammar to use for parsing
        universe: the universe to use for evaluation
        return_by_meaning: whether to return a dictionary mapping meanings to expressions or not

    Returns:
        a list of GrammaticalExpressions and a dictionary mapping meanings to expressions (empty if `return_by_meaning` is False)
    """
    if grammar is None:
        raise ValueError("A grammar must be provided to parse the expressions.")

    with open(filename, "r") as f:
        term_expressions = [line.strip() for line in f if line.strip()]

    # Re-parse the expressions using the grammar
    final_exprs = [
        grammar.parse(term_expression) for term_expression in term_expressions
    ]

    # Optionally evaluate the expressions in the given universe
    if universe is not None:
        for expr in final_exprs:
            expr.evaluate(universe)

    # Optionally create a mapping by meaning
    by_meaning = {}
    if return_by_meaning:
        by_meaning = {expr.meaning: expr for expr in final_exprs}

    return final_exprs, by_meaning


def write_languages(
    languages: list[Language],
    filename: str,
    properties_to_add: dict[str, Callable[[int, Language], Any]] = {},
) -> None:
    lang_dicts = [
        language.as_dict_with_properties(
            **{key: properties_to_add[key](idx, language) for key in properties_to_add}
        )
        for idx, language in enumerate(languages)
    ]
    with open(filename, "w+") as f:
        dump(lang_dicts, f, Dumper=Dumper)


def write_pickle(fn: str, data):
    with open(fn, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Wrote a pickle binary to {fn}.")


def read_pickle(fn: str):
    with open(fn, "rb") as f:
        data = pickle.load(f)
    return data
