"""Functions for constructing an efficient communication analysis by measuring the simplicity/informativeness trade-off languages and formatting results as a dataframe or a plot."""

import numpy as np

from ultk.language.language import Language
from typing import Any, Callable, Sequence
from tqdm import tqdm

from scipy import interpolate
from scipy.spatial.distance import cdist

##############################################################################
# Helper measurement functions
##############################################################################

# TODO: write tests!
# TODO: convert non_dominated methods to operate on numpy arrays by default?


def dominates(p1: tuple[float, ...], p2: tuple[float, ...]) -> bool:
    """Determine whether p1 dominates p2,
    i.e. whether for every i p1[i] <= p2[i]
    and for some i p1[i] < p2[i].

    Args:
        p1: a point
        p2: another point

    Returns:
        whether or not p1 dominates p2
    """
    assert len(p1) == len(p2)
    return all(p1[idx] <= p2[idx] for idx in range(len(p1))) and any(
        p1[idx] < p2[idx] for idx in range(len(p1))
    )


def non_dominated_2d(
    points: Sequence[tuple[float, float]], front_pbar: bool = False
) -> list[int]:
    """Return the non-dominated (Pareto) front of a list of 2-D points, using Kung's algorithm.

    Args:
        points: A list of 2-D points

    Returns:
        a list, the indices of `points` for which no other point is as good on all dimensions
        and better on at least one
    """
    if len(points) == 0:
        return []

    # sort list in ascending order on first dimension
    # NB: ascending order because we are assuming lower is better
    # NB: lexicographic, i.e. will sort on 2nd dim if tie on 1st dim, as desired
    # points.sort()
    indices = list(range(len(points)))
    indices.sort(key=lambda x: points[x])

    front: list[int] = []

    # Conditionally wrap `indices` with `tqdm`
    iterator = tqdm(indices, desc="finding dominant") if front_pbar else indices

    for idx in iterator:
        dominated = False
        for bot_idx in front:
            if dominates(points[bot_idx], points[idx]):
                dominated = True
                break
        if not dominated:
            front.append(idx)

    return front


def pareto_optimal_languages(
    languages: list[Language],
    objectives: list[Callable[[Language], Any]],
    unique: bool = False,
    front_pbar: bool = False,
) -> list[Language]:
    """Use non_dominated_2d to compute the Pareto languages."""
    assert len(objectives) == 2, "Can only do pareto optimization in two dimensions."
    dominating_indices = non_dominated_2d(
        tuple(
            zip(
                (objectives[0](lang) for lang in languages),
                (objectives[1](lang) for lang in languages),
            )
        ),
        front_pbar=front_pbar,
    )
    dominating_languages = [languages[idx] for idx in dominating_indices]
    return list(set(dominating_languages)) if unique else dominating_languages


def pareto_min_distances(points: list[tuple], pareto_points: list[tuple]) -> np.ndarray:
    """Measure the Pareto optimality of each language by measuring its Euclidean closeness to the frontier. The frontier is a line (list of points) interpolated from the pareto points.

    Args:

        points: the list of all language (x, y) pairs, where x and y are usually communicative cost and complexity.

        pareto_points: the list of all dominant language (x, y) pairs to constitute the Pareto frontier. The points should have been measured by pygmo's non_dominated_front_2d function.

    Returns:

        min_distances: an array of shape `len(points)` Euclidean distances for each language to the closest point on the Pareto frontier.
    """
    print("Measuring min distance to frontier ...")

    # Scale cost and complexity
    points = np.array(points)
    pareto_points = np.array(pareto_points)
    max_cost, max_complexity = points.max(axis=0)

    points[:, 0] = points[:, 0] / max_cost
    pareto_points[:, 0] = pareto_points[:, 0] / max_cost

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


def interpolate_data(
    points: list[tuple[float]], min_cost: float = 0.0, max_cost: float = 1.0, num=5000
) -> np.ndarray:
    """Interpolate the points yielded by the pareto optimal languages into a continuous (though not necessarily smooth) curve.

    Args:
        points: an list of (comm_cost, complexity) pairs of size [dominating_languages], a possibly non-smooth set of solutions to the trade-off.

        min_cost: the minimum communicative cost value possible to interpolate from.

        max_cost: the maximum communicative cost value possible to interpolate from. A natural assumption is to let complexity=0.0 if max_cost=1.0, which will result in a Pareto curve that spans the entire 2d space, and consequently the plot with x and y limits both ranging [0.0, 1.0].

        num: the number of x-axis points (cost) to interpolate. Controls smoothness of curve.

    Returns:
        interpolated_points: an array of size `(num, num)`
    """
    if max_cost == 1:
        # hack to get end of pareto curve
        points.append((1, 0))

    # NB: interp1d requires no duplicates and we require unique costs.
    points = list(
        {
            cost: comp
            for cost, comp in sorted(points, key=lambda x: x[0], reverse=True)
        }.items()
    )

    pareto_x, pareto_y = list(zip(*points))
    interpolated = interpolate.interp1d(pareto_x, pareto_y, fill_value="extrapolate")

    pareto_costs = list(set(np.linspace(min_cost, max_cost, num=num).tolist()))
    pareto_complexities = interpolated(pareto_costs)
    interpolated_points = np.array(list(zip(pareto_costs, pareto_complexities)))
    return interpolated_points


##############################################################################
# Main tradeoff function
##############################################################################


def tradeoff(
    languages: list[Language],
    properties: dict[str, Callable[[Language], Any]],
    x: str = "comm_cost",
    y: str = "complexity",
    frontier: list[tuple] = None,
) -> dict[str, list[Language]]:
    """Builds a final efficient communication analysis by measuring a list of languages, updating their internal data, and returning the results.

    This function measures possibly many graded or categorical properties of each language, but minimally the properties of commmunicative cost and complexity. These two measures fully define the results of an efficiency analysis, in the sense they define the optimal solutions.

    Args:
        languages: A list representing the pool of all languages to be measured for an efficient communication analysis.

        x: the first pressure to measure, e.g. communicative cost.

        y: the second pressure to measure, e.g. cognitive complexity.

        frontier: a list of (comm_cost, complexity) points representing a Pareto frontier to measure optimality w.r.t.

    Returns:
        a dictionary of the population and the pareto front, of the form

            {
                "languages": the list of languages, with their internal efficient communication data updated,

                "dominating_languages": the list of the languages dominating the population w.r.t. comm_cost and complexity. If no `frontier` is none, this can be considered the Pareto frontier.
            }
    """
    points = []
    for lang in tqdm(languages):
        for prop in properties:
            lang.data[prop] = properties[prop](lang)
        points.append((lang.data[x], lang.data[y]))

    dominating_languages = pareto_optimal_languages(
        languages, objectives=[properties[x], properties[y]], unique=True
    )
    dominant_points = [(lang.data[x], lang.data[y]) for lang in dominating_languages]

    if frontier is not None:
        min_distances = pareto_min_distances(points, frontier)
    else:
        min_distances = pareto_min_distances(points, dominant_points)

    print("Setting optimality ...")
    for i, lang in enumerate(tqdm(languages)):
        # warning: yaml that saves lang must use float, not numpy.float64 !
        lang.data["optimality"] = 1 - float(min_distances[i])
    return {"languages": languages, "dominating_languages": dominating_languages}
