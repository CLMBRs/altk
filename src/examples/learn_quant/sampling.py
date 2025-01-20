from ultk.language.grammar import GrammaticalExpression
from learn_quant.quantifier import QuantifierModel
import random
import numpy as np
from scipy.stats import entropy


class DatasetInitializationError(Exception):
    """Custom exception to indicate dataset initialization failure."""

    pass


def get_random_n_items(dictionary, n):
    if n > len(dictionary):
        raise ValueError("Sample size cannot be larger than the dictionary size.")
    selected_keys = random.sample(list(dictionary), n)
    return {key: dictionary[key] for key in selected_keys}


def shuffle_dictionary(dictionary):
    items = list(dictionary.items())
    random.shuffle(items)
    return dict(items)


def superimpose(array1, array2, value):
    positive_mask = array2 > 0
    array1[positive_mask] = value
    return array1


def generate_custom_array(N, X, J):

    assert 0 <= J <= X, "J must be between 0 and X (inclusive)"

    base_row = np.array([1] * J + [0] * (X - J))
    result = np.empty((N, X), dtype=int)
    for i in range(N):
        result[i] = np.random.permutation(base_row)

    return result


def generate_batch(M_size, X_size, gen_batch_size, inclusive=True):
    assert M_size <= X_size, "M_size must be less than or equal to X_size"

    if inclusive:
        M_choice = np.array(
            [np.random.choice([0, 1], gen_batch_size) for _ in range(X_size)]
        ).T
    else:
        M_choice = generate_custom_array(gen_batch_size, X_size, M_size)

    A_choice = np.array(
        [np.random.choice([0, 1], gen_batch_size) for _ in range(X_size)]
    ).T
    B_choice = np.array(
        [np.random.choice([0, 1], gen_batch_size) for _ in range(X_size)]
    ).T

    X = generate_custom_array(gen_batch_size, X_size, X_size - M_size)
    A = A_choice & M_choice
    B = B_choice & M_choice
    both = A & B & M_choice
    M = ~A & ~B & M_choice
    neither = ~A & ~B & ~M

    sample_array = np.full((gen_batch_size, X_size), 4)
    sample_array = superimpose(sample_array, A, 0)
    sample_array = superimpose(sample_array, B, 1)
    sample_array = superimpose(sample_array, both, 2)
    sample_array = superimpose(sample_array, M, 3)
    sample_array = superimpose(sample_array, neither, 4)
    if inclusive:
        sample_array = superimpose(sample_array, X, 4)

    return sample_array


def downsample_quantifier_models(expression: GrammaticalExpression):
    print("Downsampling to the smallest truth-value class for:", expression)

    # Get the truth value counts of the expressions
    value_array = expression.meaning.get_binarized_meaning()
    values, counts = np.unique(value_array, return_counts=True)
    value_counts = dict(zip(values, counts))
    sorted_counts = sorted(value_counts.items(), key=lambda x: x[1])
    assert len(sorted_counts) == 2, "Only two classes are supported"

    # Get the indices of the minimum and maximum classes
    minimum_class_indices = np.where(value_array == sorted_counts[0][0])[0]
    max_indices = np.where(value_array == sorted_counts[1][0])[0]
    maximum_class_indices = np.random.choice(
        max_indices, sorted_counts[0][1], replace=False
    )
    meaning = np.array(list(expression.meaning.mapping))

    # Combine the expressions indexed by the sampled expressions from the minimum and maximum classes / shuffle
    sampled_expressions = np.concatenate(
        [meaning[minimum_class_indices], meaning[maximum_class_indices]]
    )
    sampled_expressions = np.random.permutation(sampled_expressions)
    return sampled_expressions


def sample_by_expression(
    expression: GrammaticalExpression,
    batch_size: int,
    n_limit: int,
    M_size: int,
    X_size: int,
    entropy_threshold: float = 0.02,
    inclusive: bool = False,
):
    true_mapping = {}
    false_mapping = {}
    conditions_met = False
    counter = 0
    while not conditions_met:
        test = generate_batch(M_size, X_size, batch_size, inclusive=inclusive)
        mapping = {
            QuantifierModel(array): expression(QuantifierModel(array)) for array in test
        }
        true_mapping.update({model: val for model, val in mapping.items() if val})
        false_mapping.update({model: val for model, val in mapping.items() if not val})
        if len(true_mapping) > n_limit and len(false_mapping) > n_limit:
            conditions_met = True
        if (
            entropy(
                list(mapping.values()),
            )
            < entropy_threshold
        ):
            raise DatasetInitializationError(
                f"Entropy is too low with expression '{expression}'"
            )
        counter += 1
        if counter > 1000:
            raise DatasetInitializationError(
                "Could not find a suitable sample in 1000 iterations"
            )
    sample = get_random_n_items(true_mapping, n_limit) | get_random_n_items(
        false_mapping, n_limit
    )
    sample_shuffled = shuffle_dictionary(sample)
    return sample_shuffled
