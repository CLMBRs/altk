# Learning quantifier expressions and measuring monotonicity

The code in this example provides experimental code to:
- 1. generate universes of quantifier models, or abstract representations of different permutations of referents in expressions of specified dimensions 
- 2. exhaustively generate possible quantifier expressions for a given grammar over all quantifier models in a particular universe
- 3. train neural models to learn to verify quantifier expressions
- 4. calculate metrics given quantifier expressions, such as an entropy-based degree of monotonicity calculation and the depth of the expression
- 5. analyze and visualize . For a greater understanding of the different components of this example, follow the (tutorial)[tutorial.ipynb].

## Contents

- `scripts`: a set of scripts for generating `QuantifierModels` and measuring various properties of individual models and sets of models.  These are explained in more detail in the [Usage](#usage) section below.
    - `generate_expressions.py` - This script will reference the configuration file at `conf/config.yaml` to generate a `Universe` of the specified dimensions and generate all expressions from a defined `Grammar`. Outputs will be saved in the `outputs` folder. The script will the _shortest_ expression (ULTK `GrammaticalExpression`s) for each possible `Meaning` (set of `Referent`s) verified by licit permutations of composed functions defined in `grammar.yml`. In particular, ULTK provides methods for enumerating all grammatical expressions up to a given depth, with user-provided keys for uniqueness and for comparison in the case of a clash.  By setting the former to get the `Meaning` from an expression and the latter to compare along length of the expression, the enumeration method returns a mapping from meanings to shortest expressions which express them.
    - `learn_quantifiers.py` - This script will reference the configuration file at `conf/learn.yaml`. It loads expressions that are saved to the `output` folder after running the `generate_expressions.py` script. It transforms the data into a format that allows the training of a neural network the relationship between quantifier models and the truth values verified by a particular expression. The script then iterates through loaded expressions and uses Pytorch Lightning to train a neural model to verify randomly sampled models of particular sizes (determined by `M` and `X` parameters). Logs of parameters, metrics, and other artifacts are saved to an `mlruns` folder in directories specified by the configuration of the running `mlflow` server.
- `grammar.yml`: defines the Language of Thought grammar (a ULTK `Grammar` is created from this file in one line in `grammar.py`) for this domain, using the functions in [van de Pol 2023](https://pubmed.ncbi.nlm.nih.gov/36563568/).
- `monotonicity.py`: functions to measure degrees of monotonicity of quantifier expressions according to Section 5 of [Steinert-Threlkeld, 2021](https://doi.org/10.3390/e23101335)
- `outputs`: outputs from the generation routines for creating `QuantifierModel`s and `QuantifierUniverse`s
- `quantifier.py`: Subclasses `ultk`'s `Referent` and `Universe` classes that add additional properties and functionality for quantifier learning with `ultk`
- `sampling.py` - Functions for sampling quantifier models as training data
- `set_primitives.py` - Optional module-defined functions for primitives of the basic grammar. Not used unless specified by the `grammar.typed_rules` key
- `training.py`: `torch` classes and helper functions
- `training_lightning.py`: `lightning` classes and helper functions
- `util.py`: utility functions for I/O and other miscellani

## Usage

1. From the `src/examples` directory:
`python -m learn_quant.scripts.generate_expressions`: generates `generated_expressions.yml` files that catalog licensed `QuantifierModel`s given a `Grammar` and `QuantifierUniverse` given a config at `conf/config`

### With Slurm
2. Generate randomized index with `notebooks/randomize_expression_index.ipynb`.
3. Run `HYDRA_FULL_ERROR=1 python -m learn_quant.scripts.learn_quantifiers_slurm --multirun training.lightning=true training.strategy=multirun training.device=cpu model=mvlstm grammar.indices=false`. This command will read the config at `conf/learn_slurm` and training data based on the chosen quantifier expressions and run 1 training job per expression with the Hydra submitit plugin.

### Without Slurm
2. Run `HYDRA_FULL_ERROR=1 python -m learn_quant.scripts.learn_quantifiers training.lightning=true training.strategy=multirun training.device=cpu model=mvlstm grammar.indices=false`. This command will read the config at `conf/learn` and training data based on the chosen quantifier expressions and run 1 training job for all expressions on your local machine.
