import numpy as np

from learn_quant.meaning import create_universe
from learn_quant.util import read_expressions
from learn_quant.measures_vectorized import MonotonicityMeasurer

uni = create_universe(3,4)

expressions, _ = read_expressions("/Users/Chris/Documents/UWLing/altk/src/examples/learn_quant/outputs/M3/X4/d4/generated_expressions.yml", uni)

mm = MonotonicityMeasurer(uni, down=False)
mm(expressions)
mm.metrics["greater_than(cardinality(union(difference(A, B), difference(B, A))), cardinality(index(cardinality(A), B)))"]["monotonicity"]

sorted_monotonicity = sorted(mm.metrics.items(), key=lambda x: x[1]["monotonicity"], reverse=True)
len(sorted_monotonicity)
for x in sorted_monotonicity[0:10]:
    print(x)

len(sorted_monotonicity)

for x in range(mm.membership.shape[1]):
    upward_monotonicity_entropy(mm.submembership, mm.membership[:,x])

"""
for x in mm.membership[:,2538]:
    print(x)


for x in range(mm.submembership.shape[0]):
    print(np.dot(mm.submembership[x,:], mm.membership[:,6]))
np.dot(mm.submembership, mm.membership[:,1])

np.apply_along_axis(np.sum, 0, result)

np.matmul(mm.submembership, mm.membership[:,7])
"""


mm.submembership[0,:]


def get_preds(num_arr, num):
        """Given an array of ints, and an int, get all predecessors of the
        model corresponding to int.
        Returns an array of same shape as num_arr, but with bools
        """
        return num_arr[num,:]

def has_true_pred(num_arr, y):
    return np.any(y * num_arr)

## All degenerate
for x in range(len(mm.membership)):
    quantifier = mm.membership[:, x]
    true_preds = np.apply_along_axis(has_true_pred, 1, mm.submembership, quantifier).astype(int)
    if not np.all(true_preds):
        print(true_preds)
        print(x)


import itertools as it

def binary_to_int(arr):
    """ Converts a 2-D numpy array of 1s and 0s into integers, assuming each
    row is a binary number.  By convention, left-most column is 1, then 2, and
    so on, up until 2^(arr.shape[1]).

    :param arr: 2D numpy array
    :returns: 1D numpy array, length arr.shape[0], containing integers
    """
    return arr.dot(1 << np.arange(arr.shape[-1]))

def generate_list_models(l):
    # l is the length of the bit strings
    # returns an array with a row for each model
    indices_generator = it.chain.from_iterable(it.combinations(range(l), r) for r in range(len(range(l))+1))
    return np.array([[1 if n in indices_list else 0 for n in range(l)] for indices_list in indices_generator])



binary_to_int(generate_list_models(6))