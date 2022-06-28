"""Functions for constructing an efficient communication analysis by measuring the simplicity/informativeness trade-off languages and formatting results as a dataframe or a plot."""

import numpy as np

from altk.language.language import Language
from pygmo import non_dominated_front_2d
from typing import Callable
from tqdm import tqdm

from scipy import interpolate
from scipy.spatial.distance import cdist

##############################################################################
# Helper measurement functions
##############################################################################

def batch_measure(languages: list[Language], measures: dict[str, Callable]) -> list[Language]:
    """Measure properties of many languages at once, and modify their internal data."""
    for lang in languages:
        for m in measures:
            lang.measurements[m] = measures[m](lang)
    return languages


def pareto_optimal_languages(
    languages: list[Language], 
    x: str = "comm_cost",
    y: str = "complexity", 
    unique: bool = False,
    ) -> list[Language]:
    """Use pygmo.non_dominated_front_2d to compute the Pareto languages."""
    dominating_indices = non_dominated_front_2d(
        list(
            zip(
                [lang.measurements[x] for lang in languages],
                [lang.measurements[y] for lang in languages],
            )
        )
    )
    dominating_languages = [languages[i] for i in dominating_indices]
    return list(set(dominating_languages)) if unique else dominating_languages


def pareto_min_distances(points: list[tuple], pareto_points: list[tuple]):
    """Measure the Pareto optimality of each language by measuring its Euclidean closeness to the frontier."""
    print("Measuring min distance to frontier ...")

    # Scale complexity
    points = np.array(points)
    pareto_points = np.array(pareto_points)
    max_cost, max_complexity = points.max(axis=0)

    points[:, 1] = points[:, 1] / max_complexity
    pareto_points[:, 1] = pareto_points[:, 1] / max_complexity

    # Interpolate to get smooth frontier
    pareto_points = interpolate_data(
        [tuple(p) for p in pareto_points], max_cost=max_cost
    )

    # Measure closeness of each language to any frontier point
    distances = cdist(points, pareto_points)
    min_distances = np.min(distances, axis=1)

    # Normalize to 0, 1 because optimality is defined in terms of 1 - dist
    min_distances /= np.sqrt(2)
    return min_distances


def interpolate_data(points: list, min_cost: float=0.0, max_cost: float=1.0, num=5000) -> np.ndarray:
    """Interpolate the points yielded by the pareto optimal languages into a continuous (though not necessarily smooth) curve.

    Args:
        points: an array of size [dominating_languages], a possibly non-smooth set of solutions to the trade-off.

        min_cost: the minimum communicative cost value possible to interpolate from.

        max_cost: the maximum communicative cost value possible to interpolate from. A natural assumption is to let complexity=0.0 if max_cost=1.0, which will result in a Pareto curve that spans the entire 2d space, and consequently the plot with x and y limits both ranging [0.0, 1.0].

        num: the number of x-axis points (cost) to interpolate. Controls smoothness of curve.

    Returns:
        interpolated_points: an array of size [num, num]
    """
    if max_cost == 1:
        # hack to get end of pareto curve
        points.append((1, 0))

    # NB: interp1d requires no duplicates and we require unique costs.
    points = list({cost: comp for cost, comp in sorted(points, reverse=True)}.items())

    pareto_x, pareto_y = list(zip(*points))
    interpolated = interpolate.interp1d(pareto_x, pareto_y, fill_value="extrapolate")

    pareto_costs = list(set(np.linspace(min_cost, max_cost, num=num).tolist()))
    pareto_complexities = interpolated(pareto_costs)
    interpolated_points = np.array(list(zip(
        pareto_costs, 
        pareto_complexities,
        )))
    return interpolated_points


##############################################################################
# Main tradeoff function
##############################################################################

def tradeoff(
    languages: list[Language],
    properties: dict[str, Callable],    
    x: str = "comm_cost",
    y: str = "complexity",    
) -> dict[str, list[Language]]:
    """Builds a final efficient communication analysis of languages.

    A set of languages, measures of informativity (comm_cost) and simplicity (complexity) fully define the efficient communication results, which is the relative (near) Pareto optimality of each language. 
    
    This function also measures other properties of each language, e.g. degrees of natualness, or a categorical analogue of naturalness, as e.g. satisfaction with a semantic universal.

    This function does the following:
    Measure a list of languages, update their internal data, and return a pair of (all languages, dominant_languages).

    Args:
        languages: A list representing the pool of all languages to be measured for an efficient communication analysis.

        x: the first pressure to measure, e.g. complexity.

        y: the second pressure to measure, e.g. informativity.

    Returns:
        a dictionary of the population and the pareto front, e.g.
        {
            "languages": the list of languages, with their internal efficient communication data updated,

            "dominating_languages": the list of the Pareto optimal languages in the tradeoff.
        }
    """
    points = []
    for lang in tqdm(languages):
        for prop in properties:
            lang.measurements[prop] = properties[prop](lang)
        points.append((lang.measurements[x], lang.measurements[y]))

    dominating_languages = pareto_optimal_languages(
        languages, x, y, unique=True)
    dominant_points = [
        (lang.measurements[x], lang.measurements[y]) for lang in dominating_languages
    ]

    min_distances = pareto_min_distances(points, dominant_points)
    print("Setting optimality ...")
    for i, lang in enumerate(tqdm(languages)):
        # warning: yaml that saves lang must use float, not numpy.float64 !
        # lang.optimality = 1 - float(min_distances[i])
        lang.measurements["optimality"] = 1 - float(min_distances[i])
    return languages, dominating_languages
