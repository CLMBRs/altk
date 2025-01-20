from learn_quant.util import read_expressions
from learn_quant.quantifier import QuantifierUniverse, QuantifierModel
from learn_quant.grammar import get_indices_tag, QuantifierGrammar

from typing import Dict
import numpy as np
from copy import deepcopy
import dill as pkl
from pathlib import Path

from itertools import combinations_with_replacement, permutations

import hydra
from omegaconf import DictConfig

# e.g.:
# python -m learn_quant.monotonicity recipe=test_monotonicity
# python -m learn_quant.monotonicity recipe=4_4_5_xi grammar.indices=false


def create_universe(m_size: int, x_size: int) -> QuantifierUniverse:
    """
    Create a quantifier universe based on the given parameters.
    All references are quantifier models, which are data classes that represent a relation between sets A, B, and M.

    Args:
        m_size (int): The size of the m set.
        x_size (int): The size of the x set.

    Returns:
        QuantifierUniverse: The created quantifier universe.
    """

    possible_quantifiers = []

    for combination in combinations_with_replacement([0, 1, 2, 3], r=m_size):
        combo = list(combination) + [4] * (x_size - m_size)
        permutations_for_combo = set(permutations(combo, r=len(combo)))
        possible_quantifiers.extend(permutations_for_combo)
    possible_quantifiers_name = set(
        ["".join([str(j) for j in i]) for i in possible_quantifiers]
    )

    quantifier_models = set()
    for name in possible_quantifiers_name:
        quantifier_models.add(QuantifierModel(name=name))

    return QuantifierUniverse(
        referents=tuple(quantifier_models), m_size=m_size, x_size=x_size
    )


def binary_to_int(arr):
    """Converts a 2-D numpy array of 1s and 0s into integers, assuming each
    row is a binary number.  By convention, left-most column is 1, then 2, and
    so on, up until 2^(arr.shape[1]).

    :param arr: 2D numpy array
    :returns: 1D numpy array, length arr.shape[0], containing integers
    """
    return arr.dot(1 << np.arange(arr.shape[-1]))


def upward_monotonicity_entropy(all_models, quantifier, cfg, flip=False):
    """Measures degree of upward monotonicity of a quantifiers as
    1 - H(Q | true_pred) / H(Q) where H is (conditional) entropy, and true_pred is the
    variable over models saying whether there's a true _predecessor_ in the
    subset order.

    :param all_models: list of models
    :param quantifier: list of truth values, same len as models
    :returns scalar
    """

    quantifier = quantifier.flatten()

    if np.all(quantifier) or not np.any(quantifier):
        return 1
    # uniform distributions
    p_q_true = sum(quantifier) / len(quantifier)
    p_q_false = 1 - p_q_true
    q_ent = -p_q_true * np.log2(p_q_true) - p_q_false * np.log2(p_q_false)

    # get integers corresponding to each model
    model_ints = binary_to_int(all_models)

    def get_preds(num_arr, num, flip=False):
        """Given an array of ints, and an int, get all predecessors of the
        model corresponding to int.
        Returns an array of same shape as num_arr, but with bools
        """
        if not flip:
            return num_arr & num == num_arr
        else:
            return num_arr & num == num

    def num_preds(num_arr, num, flip=False):
        preds = get_preds(num_arr, num, flip).astype(int)
        return sum(preds)

    def has_true_pred(num_arr, quantifier, num, flip=False):
        preds = get_preds(num_arr, num, flip)
        return np.any(quantifier * preds)

    # vector of length quantifier, has a 1 if that model has a true
    # predecessor, 0 otherwise
    true_preds = np.vectorize(
        lambda num: has_true_pred(model_ints, quantifier, num, flip)
    )(model_ints).astype(int)

    # TODO: how to handle cases where true_preds is all 0s or all 1s, i.e.
    # where every model does have a true predecessor?  In that case, we have
    # H(Q | pred) = H(Q), so currently would get degree 0
    """
    if np.all(true_preds) or not np.any(true_preds):
        # to avoid divide by zeros / conditioning on zero-prob
        # TODO: does this make sense???
        print("All true_preds are the same")
        return q_ent
    """

    pred_weights = np.vectorize(lambda num: num_preds(model_ints, num, flip))(
        model_ints
    )

    # if cfg.measures.monotonicity.debug:

    """
        predecessor_prob_library = {}
        for i in range(len(model_ints)):
            predecessor_prob_library.setdefault(model_ints[i], num_preds(model_ints, i) / len(model_ints))
            print(f"Model {model_ints[i]}: {true_preds[i]}")
            print(f"Preds {model_ints[i]}: {pred_weights[i]}")
    """

    pred_prob = pred_weights / sum(pred_weights)
    # TODO: should these be weighted by pred_weights, i.e. pred_prob?
    p_pred = sum(true_preds) / len(true_preds)
    p_nopred = 1 - p_pred

    # TODO: make this elegant! solve nan problems
    q_pred = sum(quantifier * true_preds) / len(quantifier)
    q_nopred = sum(quantifier * (1 - true_preds)) / len(quantifier)
    noq_pred = sum((1 - quantifier) * true_preds) / len(quantifier)
    noq_nopred = sum((1 - quantifier) * (1 - true_preds)) / len(quantifier)

    pred_logs = np.log2(
        [noq_pred, q_pred] / p_pred, where=np.array([noq_pred, q_pred] / p_pred) > 0
    )
    pred_logs[pred_logs == -np.inf] = 0
    nopred_logs = np.log2(
        [noq_nopred, q_nopred] / p_nopred,
        where=np.array([noq_nopred, q_nopred] / p_nopred) > 0,
    )
    nopred_logs[nopred_logs == -np.inf] = 0
    ent_pred = -np.nansum(np.array([noq_pred, q_pred]) * pred_logs)
    ent_nopred = -np.nansum(np.array([noq_nopred, q_nopred]) * nopred_logs)
    cond_ent = ent_pred + ent_nopred

    # return 0 if q_ent == 0 else 1 - (cond_ent / q_ent)
    if cfg.measures.monotonicity.debug:
        print("q_ent", q_ent)
        print("p_pred", p_pred)
        print("p_nopred", p_nopred)
        print("q_pred", q_pred)
        print("q_nopred", q_nopred)
        print("noq_pred", noq_pred)
        print("noq_nopred", noq_nopred)
        print("pred_logs", pred_logs)
        print("nopred_logs", nopred_logs)
        print("ent_pred", ent_pred)
        print("ent_nopred", ent_nopred)
        print("cond_ent", cond_ent)
    return 1 - cond_ent / q_ent


def measure_monotonicity(
    all_models,
    flipped_models,
    quantifier,
    measure=upward_monotonicity_entropy,
    cfg=None,
    name=None,
):
    """Measures degree of monotonicity, as max of the degree of
    positive/negative monotonicty, for a given quantifier _and its negation_
    (since truth values are symmetric for us).

    :param all_models: list of models
    :param quantifier: list of truth values
    :param measure: method for computing degree of upward monotonicity of a Q
    :return: max of measure applied to all_models and quantifier, plus 1- each
    of those
    """

    interpretations = [
        measure(
            all_models,
            quantifier,
            cfg,
        ),  # right upward monotonicity
        measure(
            flipped_models,
            quantifier,
            cfg,
        ),  # left upward monotonicity
        # downward monotonicity
        measure(all_models, quantifier, cfg, flip=True),  # right downward monotonicity
        measure(flipped_models, quantifier, cfg, flip=True),
    ]  # left downward monotonicity

    # assert measure(all_models, quantifier, cfg,) == measure(1- all_models, quantifier, cfg, flip=True) == measure(flipped_models - both_models, quantifier, cfg, flip=True)

    print(name)
    print("\t", interpretations)

    return np.max(np.clip(interpretations, 0.0, 1.0))


def get_true_predecessors(all_models, quantifier, flip=False):

    quantifier = quantifier.flatten()

    # get integers corresponding to each model
    model_ints = binary_to_int(all_models)

    def get_preds(num_arr, num, flip):
        """Given an array of ints, and an int, get all predecessors of the
        model corresponding to int.
        Returns an array of same shape as num_arr, but with bools
        """
        if not flip:
            return num_arr & num == num_arr
        elif flip:
            return num_arr & num == num

    def num_preds(num_arr, num, flip):
        preds = get_preds(num_arr, num, flip).astype(int)
        return sum(preds)

    def has_true_pred(num_arr, quantifier, num, flip):
        preds = get_preds(num_arr, num, flip)
        return np.any(quantifier * preds)

    # vector of length quantifier, has a 1 if that model has a true
    # predecessor, 0 otherwise
    true_preds = np.vectorize(
        lambda num: has_true_pred(model_ints, quantifier, num, flip=flip)
    )(model_ints).astype(int)

    return true_preds


def filter_universe(cfg, uni):
    if cfg.measures.monotonicity.universe_filter and any(
        cfg.measures.monotonicity.universe_filter
    ):
        test_referents = tuple(
            ref
            for ref in deepcopy(uni.referents)
            if not any(
                str(digit) in ref.name
                for digit in cfg.measures.monotonicity.universe_filter
            )
        )
        print("Size of filtered universe: ", len(test_referents))
        uni = QuantifierUniverse(
            referents=test_referents,
            m_size=cfg.universe.m_size,
            x_size=cfg.universe.x_size,
        )
    return uni


def load_universe(cfg):
    try:
        uni = pkl.load(
            open(
                Path.cwd()
                / Path("learn_quant/outputs")
                / Path(cfg.measures.target)
                / Path("master_universe.pkl"),
                "rb",
            )
        )
    except FileNotFoundError:
        print("Creating universe")
        uni = create_universe(cfg.universe.m_size, cfg.universe.x_size)

    print("Size of universe: ", len(uni.referents))
    return uni


def load_grammar(cfg):
    if hasattr(cfg.grammar, "typed_rules"):
        print("Loading rules from module...")
        primitives_grammar = QuantifierGrammar.from_module(
            cfg.grammar.typed_rules.module_path
        )
        quantifiers_grammar = QuantifierGrammar.from_yaml(cfg.grammar.path)
        grammar = quantifiers_grammar | primitives_grammar
    else:
        grammar = QuantifierGrammar.from_yaml(cfg.grammar.path)
    return grammar


def get_verified_models(cfg, expressions, uni):
    print("Binarizing referents")
    all_models = uni.binarize_referents(mode="B")
    flipped_models = uni.binarize_referents(mode="A")

    # Create quantifiers like in original code
    print("Creating quantifiers")
    quantifiers = np.array(
        [
            [
                expression.meaning.mapping[uni.referents[x]]
                for x in range(len(uni.referents))
            ]
            for expression in expressions
        ],
        dtype=int,
    )
    expression_names = np.array(
        [expression.term_expression for expression in expressions]
    )
    return all_models, flipped_models, quantifiers, expression_names


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:

    uni = load_universe(cfg)
    # Filter out referents with certain digits in their names (e.g. 3, 4)
    uni = filter_universe(cfg, uni)

    grammar = load_grammar(cfg)

    print("Reading expressions")

    indices_tag = get_indices_tag(indices=cfg.grammar.indices)
    expressions, _ = read_expressions(
        Path.cwd()
        / Path("learn_quant/outputs")
        / Path(cfg.measures.target)
        / f"generated_expressions{indices_tag}.yml",
        uni,
        add_indices=cfg.grammar.indices,
        grammar=grammar,
    )

    # All models should not use binarize referents, but "get_truth_matrix"
    # Use b only and both?
    all_models, flipped_models, quantifiers, expression_names = get_verified_models(
        cfg, expressions, uni
    )

    # Select only quantifiers in the expression list (unless 'all' specified)
    if "all" not in cfg.measures.expressions:
        mask = np.isin(expression_names, cfg.measures.expressions)
        indices = np.where(mask)[0]
        quantifiers = quantifiers[indices]
        expression_names = expression_names[indices]

    print("Measuring monotonicity")

    if "all" in cfg.measures.monotonicity.direction:
        mon_values = np.empty(shape=(len(quantifiers), 1))
        for i in range(len(quantifiers)):
            mon_values[i] = measure_monotonicity(
                all_models,
                flipped_models,
                quantifiers[i],
                upward_monotonicity_entropy,
                cfg,
                name=expression_names[i],
            )
        order_indices = np.argsort(mon_values, axis=0)[::-1]
        print("Monotonicity values len:", len(mon_values))
        print("expression_names len:", len(expression_names))
        print("quantifiers len:", len(quantifiers))
        outputs = [
            (expression_name, quantifier, mon_value)
            for expression_name, quantifier, mon_value in zip(
                expression_names[order_indices].tolist(),
                quantifiers[order_indices].tolist(),
                mon_values[order_indices].tolist(),
            )
        ]
        for x in outputs:
            print(x[0], " : ", x[2])


if __name__ == "__main__":
    main()
