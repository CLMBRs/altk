# Learning quantifier expressions and measuring monotonicity

This example is under ongoing development.

The code in this example generates models of quantifier expressions for testing their learnability. For a greater understanding of the different components of this example, follow the (tutorial)[tutorial.ipynb].

## Contents

- `scripts`: a set of scripts for generating `QuantifierModels` and measuring various properties of individual models and sets of models.  These are explained in more detail in the [Usage](#usage) section below.
- `outputs`: outputs from the generation routines for creating `QuantifierModel`s and `QuantifierUniverse`s
- `referents.csv`: this file defines the set of points of communication (which will become `Referent`s in ULTK terms).
- `meaning.py`: this file defines the meaning space (a `Universe` in ULTK terms) of referents that are individual models of quantifiers (`QuantifierModel`s)
- `quantifier.py`: defines the subclasses of `ultk`'s `Referent` and `Universe` classes that add additional properties and functionality for modeling quantifier learning
- `grammar.yml`: defines the Language of Thought grammar (an ULTK `Grammar` is created from this file in one line in `grammar.py`) for this domain, using the five semantic features identified in Haspelmath 1997.
- `measures.py`: functions to measure monotonicity of quantifiers according to different methods
- `util.py`: utilities for reading and writing ULTK `Expression`s and `Language`s, as well as the natural language data.

## Usage

From the `src/examples` directory:
1. `python -m learn_quant.scripts.generate_expressions`: generates `generated_expressions.yml` files that catalog licensed `QuantifierModel`s given a `Grammar` and `QuantifierUniverse`

    This script generates the _shortest_ expression (ULTK `GrammaticalExpression`s) for each possible `Meaning` (set of `Referent`s) in the LoT defined in `grammar.py`. In particular, ULTK provides methods for enumerating all grammatical expressions up to a given depth, with user-provided keys for uniqueness and for comparison in the case of a clash.  By setting the former to get the `Meaning` from an expression and the latter to compare along length of the expression, the enumeration method returns a mapping from meanings to shortest expressions which express them.

2. `python -m learn_quant.scripts.generation_text`: generates a `GrammaticalExpression` from the quantifier modeling `Grammar`

## Comparison to "Learnability and semantic universals" (Steinert-Threlkeld and Szymanik 2019)

This example attempts to generalize the experiments from Steinert-Threlkeld and Szymanik 2019 to observe learnability properties across a wide range of quantifiers, both hypothetical and evinced in natural expressions. 

## TODOs for this example

1. Add configuration files (ideally yml using [hydra](https://hydra.cc)), to keep track of filenames and allow for easy experimentation with different parameter settings.
2. Measure monotonicity and run statistical tests in `scripts/monotonicity.py`.
3. ...