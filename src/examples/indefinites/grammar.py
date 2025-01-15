from ultk.language.grammar import Grammar, Rule
import pandas as pd
from ultk.language.semantics import Universe

referents = pd.read_csv("indefinites/referents.csv")
prior = pd.read_csv("indefinites/data/Beekhuizen_priors.csv")
assert (referents["name"] == prior["name"]).all()
referents["probability"] = prior["probability"]
universe = Universe.from_dataframe(referents)

indefinites_grammar = Grammar.from_yaml("indefinites/grammar.yml")
#indefinites_grammar = Grammar.from_module("indefinites.grammar_functions")
print(indefinites_grammar.parse("and(not(K+), or(N-, not(SE-)))").hm_sample(indefinites_grammar, [(universe.referents[2], True)]))

"""
# this defines the grammar "manually" instead of using the YAML text format

indefinites_grammar = Grammar(bool)
# basic propositional logic
indefinites_grammar.add_rule(Rule("and", bool, (bool, bool), lambda p1, p2: p1 and p2))
indefinites_grammar.add_rule(Rule("or", bool, (bool, bool), lambda p1, p2: p1 or p2))
indefinites_grammar.add_rule(Rule("not", bool, (bool,), lambda p1: not p1))


# primitive features
# We include "positive" and "negative" features as primitives (instead of definining the latter via negation) for two reasons.
# (1) Conceptually, it's not clear that the positive ones are any more basic than the negative ones.  But defining them in
# terms of negation would make them more complex according to our measure.
# (2) Computationally, this greatly shrinks the space of grammatical expressions that need to be explored before finding one
# that expresses each meaning.  Better search and/or minimization algorithms would help here.
indefinites_grammar.add_rule(
    Rule("K+", bool, None, lambda point: point.name == "specific-known")
)
indefinites_grammar.add_rule(
    Rule("K-", bool, None, lambda point: point.name != "specific-known")
)
indefinites_grammar.add_rule(
    Rule(
        "S+",
        bool,
        None,
        lambda point: point.name in ("specific-known", "specific-unknown"),
    )
)
indefinites_grammar.add_rule(
    Rule(
        "S-",
        bool,
        None,
        lambda point: point.name not in ("specific-known", "specific-unknown"),
    )
)
indefinites_grammar.add_rule(
    Rule(
        "SE+",
        bool,
        None,
        lambda point: point.name in ("npi", "freechoice", "negative-indefinite"),
    )
)
indefinites_grammar.add_rule(
    Rule(
        "SE-",
        bool,
        None,
        lambda point: point.name not in ("npi", "freechoice", "negative-indefinite"),
    )
)
indefinites_grammar.add_rule(
    Rule("N+", bool, None, lambda point: point.name == "negative-indefinite")
)
indefinites_grammar.add_rule(
    Rule("N-", bool, None, lambda point: point.name != "negative-indefinite")
)
# NB: the grammar should be modified in such a way that R+ and R- can only occur with SE+
# easiest would be to just split SE+ into two features
# more elegant: extra grammar rule (will preserve the impact on complexity)
indefinites_grammar.add_rule(
    Rule("R+", bool, None, lambda point: point.name in ("negative-indefinite", "npi"))
)
indefinites_grammar.add_rule(
    Rule("R-", bool, None, lambda point: point.name == "freechoice")
)
"""
