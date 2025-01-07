# Indefinite Pronouns Optimize the Simplicity/Informativeness Trade-Off

See [the paper](https://doi.org/10.1111/cogs.13142) and [the corresponding original repo](https://github.com/milicaden/indefinite-pronouns-simplicity-informativeness).

This README will continue to be updated!

This example creates a "conceptual" / miniature replication of the above paper using the tools provided by the ULTK library.  Right now, the final analysis produces the following plot:
![a plot showing communicative cost and complexity of natural, explored, and dominant languages](https://github.com/CLMBRs/altk/blob/main/src/examples/indefinites/outputs/plot.png?raw=true)

This README first explains the contents of this example directory, focusing on what the user has to provide that's specific to the indefinites case study, before then explaining the concrete steps taken to produce the above plot.  After that, there is some discussion of what's missing from the above paper and other next steps for this example.

## Contents

- `data`: various pieces of data to be used in the analysis
    - `raw/languages_real_40_updated.csv`: this contains Haspelmath's 40 language sample of indefinite systems, as compiled by Bill Croft.  Each row corresponds to an expression, with columns for (i) ontological category (e.g. person) and then (ii) the nine functions from Haspelmath 1997.  Annotations for `PERSON`, `DETER`, and `neg.frag` were added by Milica Denic (see appendices in the above repo). Expressions/items are named with a number for language and a letter indicating the expression.  For example, `03s` corresponds to "some-": `03` is for English and `s` means the "some"-series.
    - `Beekhuizen_prior.csv`: the prior distribution over semantic flavors, estimated from the annotated corpus of Beekhuizen et al 2017
    - `natural_language_indefinites.csv`: a cleaned version of the raw data above (see item 1 in the [Usage](#usage) section below)
- `scripts`: a set of scripts for executing various components of the efficient communication analysis.  These are explained in more detail in the [Usage](#usage) section below.
- `outputs`: outputs from the analysis scripts
- `referents.csv`: this file defines the set of points of communication (which will become `Referent`s in ULTK terms).

    This is a very simple example, with six discrete points which have only on property (a name).  In general, ULTK expects each row to correspond to a unique `Referent` and each column to a feature of that point, with no constraint on the number or type of features.  A `name` column is expected.  See `ultk.language.semantics.Universe.from_dataframe` for more details.
- `meaning.py`: this file defines the meaning space (a `Universe` in ULTK terms) of the six flavors defined in `referents.csv` together with their prior
- `grammar.yml`: defines the Language of Thought grammar (an ULTK `Grammar` is created from this file in one line in `grammar.py`) for this domain, using basic propositional logic and the five semantic features identified in Haspelmath 1997.
- `measures.py`: the measures of simplicity and informativity.  These are basic wrappers around tools from ULTK, linking them to the indefinites grammar and universe.
- `util.py`: utilities for reading and writing ULTK `Expression`s and `Language`s, as well as the natural language data.

## Usage

From the `src/examples` directory:
1. `python -m indefinites.scripts.convert_haspelmath`: consumes `data/raw/languages_real_40_updated.csv` and generates `data/natural_language_indefinites.csv`.

    It primarily transforms Haslpemath's functions into our six semantic flavors, as outlined in the paper linked above (along with a few other cleaning things).
2. `python -m indefinites.scripts.generate_expressions`: generates `outputs/generated_expressions.yml`

    This script generates the _shortest_ expression (ULTK `GrammaticalExpression`s) for each possible `Meaning` (set of `Referent`s) in the LoT defined in `grammar.py`. In particular, ULTK provides methods for enumerating all grammatical expressions up to a given depth, with user-provided keys for uniqueness and for comparison in the case of a clash.  By setting the former to get the `Meaning` from an expression and the latter to compare along length of the expression, the enumeration method returns a mapping from meanings to shortest expressions which express them.
3. `python -m indefinites.scripts.estimate_pareto`: consumes `outputs/generated_expressions.yml` and generates `outputs/dominating_languages.yml` and `outputs/explored_languages.yml`

    This calls `ultk.effcomm.EvolutionaryOptimizer.fit` to use an evolutionary algorithm to esimate the Pareto frontier.  For simplicity, it uses the default mutations of simply adding and removing an expression from a language.  `dominating_languages.yml` contains the Pareto optimal languages, while `explored_languages.yml` contains all languages generated during the optimization process.
4. `python -m indefinites.scripts.measure_natural_languages`: consumes `data/natural_language_indefinites.csv`, `outputs/generated_expressions.yml` and generates `outputs/natural_languages.yml`

    This measures complexity and communicative cost of the 40 natural languages and writes them to `natural_languages.yml`.
5. `python -m indefinites.scripts.combine_data`: consumes `outputs/*_languages.yml` and generates `outputs/combined_data.csv`

    The resulting CSV containing data from all of the languages generated so far. It is a table with columns for language name, type (natural, explored, dominant), complexity, and communicative cost, with each row being a language.
6. `python -m indefinites.scripts.analyze`: consumes `outputs/combined_data.csv` and generates `outputs/plot.png`

    For now, this simply reads in the data and generates a complexity-cost trade-off plot, showing where the natural, explored, and dominant languages lie.  Soon, it will include more thorough statistical analyses.

## Comparison to Denic et al 2022

This example is a kind of "minimal" replication of Experiment 1 from Denic et al 2022.  Because the primary focus of this reproduction is to demonstrate how to use ULTK and its primitives, there are some differences to keep in mind.
1. We have not here implemented the controls for coverage and synonymy that are used in the paper.  These could, however, easily be added by reading in `outputs/explored_languages.yml`, applying the optimization algorithm from the paper, and re-writing the subset of languages back out.
2. We have used only 3-operator complexity (not 2-operator complexity).  Additionally, we have not added the restriction that the `R` features in the grammar can only occur with `SE+`.  See the discussion in the comments in `grammar.py` for more information.
3. We have not done the analyses with pragmatic speakers and listeners.  ULTK, however, makes this very easy to do!  See `ultk.effcomm.agent.PragmaticSpeaker` and `ultk.effcomm.agent.PragmaticListener`.  In particular, the `ultk.effcomm.informativity.informativity` method that we use takes an argument `agent_type`.  It defaults to "literal"; but passing in `agent_type="pragmatic"` to this method in the `estimate_pareto` and `measure_natural_languages` scripts would measure with pragmatic agents.

## TODOs for this example

1. Add configuration files (ideally yml using [hydra](https://hydra.cc)), to keep track of filenames and allow for easy experimentation with different parameter settings.
2. Measure optimality and run statistical tests in `scripts/analyze.py`.
3. ...