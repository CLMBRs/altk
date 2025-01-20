from time import time
from copy import deepcopy
import os
import csv
import pathlib
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from ultk.language.grammar import GrammaticalExpression
from ultk.language.semantics import Meaning
from typing import Any

from ..quantifier import QuantifierUniverse
from ..grammar import QuantifierGrammar, add_indices
from ..monotonicity import create_universe
from ..util import save_quantifiers, save_inclusive_generation

# e.g.:
# python -m learn_quant.scripts.generate_expressions mode=generate universe.inclusive_universes=false universe.m_size=4 universe.x_size=5 grammar.depth=3 recipe=base grammar.indices=true
# HYDRA_FULL_ERROR=1 python -m learn_quant.scripts.generate_expressions mode=time_trial recipe=base


def enumerate_quantifiers(
    depth: int,
    quantifiers_universe: QuantifierUniverse,
    quantifiers_grammar: QuantifierGrammar,
) -> dict[GrammaticalExpression, Any]:

    expressions_by_meaning: dict[Meaning, GrammaticalExpression] = (
        quantifiers_grammar.get_unique_expressions(
            depth,
            max_size=2 ** len(quantifiers_universe),
            unique_key=lambda expr: expr.evaluate(quantifiers_universe),
            compare_func=lambda e1, e2: len(e1) < len(e2),
        )
    )

    # filter out the trivial meaning, results in NaNs
    # iterate over keys, since we need to change the dict itself
    for meaning in list(expressions_by_meaning.keys()):
        if meaning.is_uniformly_false():
            del expressions_by_meaning[meaning]

    return expressions_by_meaning


def generate_expressions(
    quantifiers_grammar: QuantifierGrammar,
    cfg: DictConfig,
    universe: QuantifierUniverse = None,
):

    quantifiers_grammar, indices_tag = add_indices(
        quantifiers_grammar,
        indices=cfg.grammar.indices,
        m_size=cfg.universe.m_size,
        weight=cfg.grammar.weight,
    )

    if not universe:
        quantifiers_universe = create_universe(cfg.universe.m_size, cfg.universe.x_size)
    else:
        quantifiers_universe = universe
    expressions_by_meaning = enumerate_quantifiers(
        cfg.grammar.depth, quantifiers_universe, quantifiers_grammar
    )

    parent_dir = (
        Path().cwd()
        / Path(cfg.output)
        / Path("M" + str(cfg.universe.m_size))
        / Path("X" + str(cfg.universe.x_size))
        / Path("d" + str(cfg.grammar.depth))
    )
    if cfg.save:
        save_quantifiers(
            expressions_by_meaning,
            parent_dir,
            universe=quantifiers_universe,
            indices_tag=indices_tag,
        )
    else:
        return expressions_by_meaning


def generation_time_trial(quantifiers_grammar: QuantifierGrammar, cfg: DictConfig):

    if cfg.time_trial_log:
        time_log = pathlib.Path(cfg.output) / pathlib.Path(cfg.time_trial_log)
    else:
        time_log = pathlib.Path(cfg.output) / pathlib.Path(
            "generated_expressions_time_log.csv"
        )

    # Remove old time log
    if os.path.exists(time_log):
        os.remove(time_log)

    # Flush times as they are output to time log
    with open(time_log, "a+", newline="") as f:

        writer = csv.writer(f)
        writer.writerow(
            [
                "m_size",
                "x_size",
                "depth",
                "universe_size",
                "elapsed_time_enumerate",
                "elapsed_time_creation",
            ]
        )
        f.flush()

        for m_size in range(1, cfg.universe.m_size + 1):

            print(
                "Generating a universe where x_size={} and m_size={}.".format(
                    cfg.universe.x_size, m_size
                )
            )

            # Ensure that primitives are added to the grammar up to `m_size`
            quantifiers_grammar_at_depth = deepcopy(quantifiers_grammar)
            quantifiers_grammar_at_depth, indices_tag = add_indices(
                quantifiers_grammar_at_depth,
                indices=cfg.grammar.indices,
                m_size=m_size,
                weight=cfg.grammar.weight,
            )
            print(quantifiers_grammar_at_depth)

            # Create the universe
            creation_start = time()
            quantifier_universe = create_universe(m_size, cfg.universe.x_size)
            creation_elapsed = time() - creation_start
            print("The size of the universe is {}".format(len(quantifier_universe)))

            # Don't consider depth=1, as depth is not deep enough to generate and expression
            for depth in range(2, cfg.grammar.depth + 1):

                enumeration_start = time()
                print("msize: ", m_size)
                print("depth: ", depth)

                expressions_by_meaning = enumerate_quantifiers(
                    depth, quantifier_universe, quantifiers_grammar_at_depth
                )

                enumerate_elapsed = time() - enumeration_start
                print(enumerate_elapsed)
                print("")

                from pathlib import Path

                parent_dir = (
                    Path(cfg.output)
                    / Path("M" + str(m_size))
                    / Path("X" + str(cfg.universe.x_size))
                    / Path(str("d" + str(depth)))
                )
                Path(parent_dir).mkdir(parents=True, exist_ok=True)

                if cfg.save:
                    print("Saving generated expressions...")
                    save_quantifiers(
                        expressions_by_meaning,
                        parent_dir,
                        universe=quantifier_universe,
                        indices_tag=indices_tag,
                    )

                writer.writerow(
                    [
                        m_size,
                        cfg.universe.x_size,
                        depth,
                        len(quantifier_universe),
                        enumerate_elapsed,
                        creation_elapsed,
                    ]
                )
                f.flush()


def generate_inclusive_expressions(quantifiers_grammar, cfg, save=True):
    # Flush times as they are output to time log
    master_universe = None
    depth = cfg.grammar.depth

    # Don't consider m_size=0, as this is the trivial meaning
    for m_size in range(1, cfg.universe.m_size + 1):

        print(
            "Generating a universe where x_size={} and m_size={}.".format(
                cfg.universe.x_size, m_size
            )
        )

        # Ensure that primitives are added to the grammar up to `m_size`
        quantifiers_grammar_at_depth = deepcopy(quantifiers_grammar)
        quantifiers_grammar_at_depth, indices_tag = add_indices(
            quantifiers_grammar_at_depth,
            indices=cfg.grammar.indices,
            m_size=m_size,
            weight=cfg.grammar.weight,
        )
        print(quantifiers_grammar_at_depth)

        # Create the universe
        creation_start = time()
        quantifier_universe = create_universe(m_size, cfg.universe.x_size)
        creation_elapsed = time() - creation_start
        print("The size of the universe is {}".format(len(quantifier_universe)))

        if not master_universe:
            master_universe = quantifier_universe
        else:
            master_universe += quantifier_universe

        enumeration_start = time()
        print("maximum_msize: ", m_size)
        print("depth: ", depth)

        expressions_by_meaning = enumerate_quantifiers(
            depth, master_universe, quantifiers_grammar_at_depth
        )

        enumerate_elapsed = time() - enumeration_start
        print(enumerate_elapsed)
        print("")
        if save:
            save_inclusive_generation(
                expressions_by_meaning,
                master_universe,
                cfg.output,
                m_size,
                cfg.universe.x_size,
                cfg.grammar.depth,
                indices_tag=indices_tag,
            )


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(cfg: DictConfig) -> None:
    print(OmegaConf.to_yaml(cfg))

    if hasattr(cfg.grammar, "typed_rules"):
        primitives_grammar = QuantifierGrammar.from_module(
            cfg.grammar.typed_rules.module_path
        )
        print(cfg.grammar.path)
        quantifiers_grammar = QuantifierGrammar.from_yaml(cfg.grammar.path)
        grammar = quantifiers_grammar | primitives_grammar
    else:
        grammar = QuantifierGrammar.from_yaml(cfg.grammar.path)

    from pprint import pprint

    pprint(grammar._rules)

    if cfg.universe.inclusive_universes:
        # Generate expressions for universes up to size M
        generate_inclusive_expressions(grammar, cfg)
    elif "time_trial" in cfg.mode:
        # Time the generation of expressions for universes up to size M and depths up to D at fixed X
        generation_time_trial(grammar, cfg)
    elif "generate" in cfg.mode:
        # Generate expressions for a single universe at size M
        generate_expressions(grammar, cfg)


if __name__ == "__main__":
    main()
