import pandas as pd
from learn_quant.quantifier import QuantifierModel, QuantifierUniverse
from itertools import product, combinations_with_replacement, permutations
from ultk.language.sampling import powerset
import random
import argparse

def create_universe(M_SIZE, X_SIZE):

    possible_quantifiers = []

    for x in combinations_with_replacement([0,1,2,3], r=M_SIZE):
        combo = list(x) + [4] * (X_SIZE-M_SIZE)
        permutations_for_combo = set(permutations(combo, r=len(combo)))
        possible_quantifiers.extend(permutations_for_combo)
    possible_quantifiers_name = set(["".join([str(j) for j in i]) for i in possible_quantifiers])

    quantifier_models = set()
    for name in possible_quantifiers_name:
        quantifier_models.add(QuantifierModel(name=name))
    return QuantifierUniverse(quantifier_models, M_SIZE, X_SIZE)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate expressions')
    parser.add_argument('--m_size', type=int, default=8, help='maximum size of the universe')
    parser.add_argument('--x_size', type=int, default=8, help='number of unique referents from which M may be comprised')

    args = parser.parse_args()

    quantifier_universe = create_universe(M_SIZE, X_SIZE)
    print("The size of the universe is {}".format(len(quantifier_universe)))
    