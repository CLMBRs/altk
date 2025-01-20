from typing import Any

import dill as pkl
import random
import os
from pathlib import Path

from ultk.language.grammar import GrammaticalExpression
from ultk.language.language import Expression
from ultk.language.semantics import Meaning, Universe
from ultk.util.io import write_expressions, read_grammatical_expressions

from learn_quant.grammar import quantifiers_grammar
from learn_quant.quantifier import QuantifierUniverse


def summarize_expression(expression: GrammaticalExpression):
    print(str(expression))
    sample = random.sample(list(expression.meaning.mapping), 10)
    for model in sample:
        print(model, expression.meaning.mapping[model])


def read_expressions(
    filename: str,
    universe: Universe = None,
    return_by_meaning=True,
    pickle=False,
    add_indices=True,
    grammar=None,
) -> tuple[list[GrammaticalExpression], dict[Meaning, Expression]]:
    """
    Read expressions from a PKL or YAML file.

    Args:
        filename (str): The path to the YAML file containing the expressions.
        universe (Universe, optional): The universe object to evaluate the expressions against. Defaults to None.
        return_by_meaning (bool, optional): Whether to return the expressions as a dictionary with meanings as keys. Defaults to True.

    Returns:
        tuple[list[GrammaticalExpression], dict[Meaning, Expression]]: A tuple containing the parsed expressions and, if return_by_meaning is True, a dictionary of expressions by their meanings.
    """

    if pickle:
        expression_list = pkl.load(open(filename, "rb"))
    else:
        if not grammar:
            grammar = quantifiers_grammar
        if add_indices:
            grammar.add_indices_as_primitives(universe.x_size)
            print("Indices added as primitives to the grammar.")

        parsed_exprs, by_meaning = read_grammatical_expressions(filename, grammar)
    return parsed_exprs, by_meaning


def filter_expressions_by_rules(rules: list, expressions):
    """
    Filters a list of expressions based on a set of rules.

    Args:
        rules (list): A list of rules to filter the expressions.
        expressions: The list of expressions to be filtered.

    Returns:
        list: A filtered list of expressions that match the given rules.
    """
    return list(filter(lambda x: str(x) in rules, expressions))


def read_expressions_from_folder(
    folder: str,
    return_by_meaning=True,
    grammar=None,
) -> tuple[list[GrammaticalExpression], dict[Meaning, Expression]]:
    """Read expressions from a YAML file in a specified folder.

    Args:
        folder (str): The path to the folder containing the expressions file and the universe file.
        return_by_meaning (bool, optional): Whether to return the expressions as a dictionary with meanings as keys. Defaults to True.

    Returns:
        tuple[list[GrammaticalExpression], dict[Meaning, Expression]]: A tuple containing the parsed expressions, a dictionary of expressions by meaning, and the universe object.

    Raises:
        FileNotFoundError: If the expressions file or the universe file is not found.
    """

    expressions_file = os.path.join(
        folder, "generated_expressions.yml"
    )  # replace 'filename.yaml' with your actual filename
    universe_file = os.path.join(
        folder, "master_universe.pkl"
    )  # replace 'universe.pkl' with your actual universe filename

    with open(universe_file, "rb") as f:
        universe = pkl.load(f)

    if not grammar:
        grammar = quantifiers_grammar

    grammar.add_indices_as_primitives(universe.x_size)

    parsed_exprs, by_meaning = read_grammatical_expressions(expressions_file, grammar)
    return parsed_exprs, by_meaning, universe


def save_quantifiers(
    expressions_by_meaning: dict[GrammaticalExpression, Any],
    parent_dir: str,
    universe: QuantifierUniverse = None,
    indices_tag: str = "",
    pickle: bool = True,
):
    """
    Save the quantifiers expressions to a YAML file.

    Args:
        expressions_by_meaning (dict): A dictionary mapping GrammaticalExpression objects to their corresponding meanings.
        out_path (str, optional): The output file path. Defaults to "generated_expressions.yml".
    """

    out_path = f"generated_expressions{indices_tag}.yml"
    print("Saving generated expressions to file...")
    print("Output path:", Path(parent_dir) / Path(out_path))

    # Create all necessary parent directories if there's a directory path
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    write_expressions(
        expressions_by_meaning.values(), Path(parent_dir) / Path(out_path)
    )

    pickle_output_file = parent_dir / f"generated_expressions{indices_tag}.pkl"

    # Open the file in write binary mode and dump the object
    if pickle:
        with open(pickle_output_file, "wb") as f:
            pkl.dump(expressions_by_meaning, f)

    if universe:
        # Create a new path for the pickle file
        universe_path = f"master_universe.pkl"
        universe_output_file = parent_dir / universe_path

        # Open the file in write binary mode and dump the object
        with open(universe_output_file, "wb") as f:
            pkl.dump(universe, f)

        print("Master universe has been pickled and saved to", pickle_output_file)

    print(
        "Expressions have been YAML'ed to {} and PKL'ed to {}".format(
            out_path, pickle_output_file
        )
    )


def save_inclusive_generation(
    expressions_by_meaning: dict[GrammaticalExpression, Any],
    master_universe: QuantifierUniverse,
    output_dir: str,
    m_size: int,
    x_size: int,
    depth: int,
    indices_tag: str,
):
    """
    Save the generated expressions and the master universe to files.

    Args:
        expressions_by_meaning (dict[GrammaticalExpression, Any]): A dictionary mapping GrammaticalExpressions to their meanings.
        master_universe (QuantifierUniverse): The master universe object.
        output_dir (str): The directory where the files will be saved.
        m_size (int): The size of M.
        x_size (int): The size of X.
        depth (int): The depth of the generated expressions.

    Returns:
        None
    """

    output_file = Path(output_dir) / Path(
        "inclusive/"
        + "M"
        + str(m_size)
        + "_"
        + "X"
        + str(x_size)
        + "_"
        + str("d" + str(depth))
    )
    Path(output_file).mkdir(parents=True, exist_ok=True)

    print("Saving generated expressions...")
    save_quantifiers(
        expressions_by_meaning,
        output_file,
        universe=master_universe,
        indices_tag=indices_tag,
    )


def calculate_term_expression_depth(expression):
    depth = 0
    max_depth = 0
    for char in expression:
        if char == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif char == ")":
            depth -= 1
    return max_depth
