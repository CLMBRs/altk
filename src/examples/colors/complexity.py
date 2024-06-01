import os
import math
import pickle
import plotnine as pn
import pandas as pd
from ultk.language.language import Language
import ultk.language.sampling as sampling
import ultk.effcomm.rate_distortion as rd
import numpy as np


def generate_ib_bound(meaning, prior, ib_start=-2, ib_stop=5, ib_step=100):
    """Generate a DataFrame corresponding to the information boundary for the given meaning and prior.

    Caches the result to a local file, and reads from/to it.

    Args:
        meaning (np.ndarray): Matrix representing the meaning distribution.
        prior (np.ndarray): Matrix representing the prior distribution.
    """

    # Set up the values to be checked for the IB bound based on log spaced values
    betas = np.logspace(ib_start, ib_stop, ib_step)
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # If a cached version of the IB bound already exists, load it
    ib_bound_filename = (
        f"{current_dir}/outputs/ib_bound_{ib_start}_{ib_stop}_{ib_step}.pkl"
    )
    if os.path.exists(ib_bound_filename):
        with open(ib_bound_filename, "rb") as f:
            print(f"Loading information bound from file:{ib_bound_filename}")
            ib_boundary = pickle.load(f)
    else:
        # if(USE_NOGA_ARRAYS):
        #     ib_boundary = rd.get_ib_bound(prior=noga_prior, meaning_dists=noga_meaning_dists, betas=betas)
        # else:
        # ib_boundary = ultk.rate_distortion
        ib_boundary = rd.get_ib_bound(prior=prior, meaning_dists=meaning, betas=betas)
        # Save the IB bound to a file
        with open(ib_bound_filename, "wb") as f:
            pickle.dump(ib_boundary, f)

    ib_boundary_points = pd.DataFrame(
        [
            (
                "ib_bound",
                "ib_bound",
                ib_point.rate,
                ib_point.accuracy,
                ib_point.distortion,
            )
            for ib_point in ib_boundary
            if ib_point is not None
        ],
        columns=["name", "type", "complexity", "informativity", "comm_cost"],
    )
    ib_boundary_points.to_csv(f"{current_dir}/outputs/ib_bound.csv")

    return ib_boundary_points


def generate_color_complexity(
    nat_langs, art_langs, meaning_dist, prior, use_rkk=False, generate_ib_bound=False
):
    """
    Generate the complexity data for the color languages
    Args:
        nat_langs (list[Language]): List of natural languages to be analyzed.
        art_langs (list[Language]): List of artificial languages to be analyzed.
        meaning_dist (nparray): Meaning distribution of the color universe.
        generate_ib_bound (bool, optional): True to generate the IB bound for the specified parameters. Defaults to False.
        use_rkk (bool, optional): True to use the RKK metric for complexity, instead of RKK+ default. Defaults to False.
    """

    current_dir = os.path.dirname(os.path.realpath(__file__))
    import matplotlib.pyplot as plt

    # Generate the imshow heatmap for the meaning
    plt.imshow(meaning_dist, cmap="hot")
    plt.savefig(f"{current_dir}/outputs/meaning_dists.jpg")

    current_dir = os.path.dirname(os.path.realpath(__file__))
    if nat_langs is None or art_langs is None:
        print("Natural languages not provided, reading from file")
        nat_langs: dict[str, Language] = pickle.load(
            open(f"{current_dir}/outputs/natural-languages.pkl", "rb")
        )
        art_langs: dict[str, Language] = pickle.load(
            open(f"{current_dir}/outputs/artificial-languages.pkl", "rb")
        )

    # Generate the meaning/accuracy/complexity for all languages based on the prior, meaning and Language
    language_data = []
    for language in nat_langs:
        # Dereference the lang code to get the actual language associated with it
        language_name = language.name
        lang_code = int(language.lang_code)
        # Exclude the languages Amuzgo, Camsa, Candoshi, Chayahuita, Chiquitano, Cree, Garífuna (Black Carib), Ifugao, Micmac, Nahuatl, Papago (O’odham), Slave, Tacana, Tarahumara (Central), Tarahumara (Western).
        # These languages have fewer than 5 definitions for major terms
        excluded_language_codes = [
            7,
            19,
            20,
            25,
            27,
            31,
            38,
            48,
            70,
            78,
            80,
            88,
            91,
            92,
            93,
        ]
        uniform_prior = np.array([1 / len(meaning_dist)] * len(meaning_dist))

        if lang_code not in excluded_language_codes:
            # RKK - complexity is the number of color terms in the language, otherwise it's the log
            ib_point = rd.language_to_ib_point(
                language=language, prior=uniform_prior, meaning_dists=(meaning_dist)
            )

            if use_rkk:
                language_data.append(
                    (
                        language_name,
                        "natural",
                        (len(language.expressions)),
                        ib_point[1],
                        ib_point[2],
                    )
                )
            else:
                # Use just the information bound metric
                language_data.append(
                    (
                        language_name,
                        "natural",
                        math.log(len(language.expressions)),
                        ib_point[1],
                        ib_point[2],
                    )
                )

    # Analyze each of the artificial languages
    artificial_lang_count = 0
    for artificial_language in art_langs:
        artificial_lang_count += 1
        # if USE_NOGA_ARRAYS:
        #     artificial_ib_point =  rd.language_to_ib_point(language=artificial_language, prior=noga_prior, meaning_dists=(noga_meaning_dists))
        # else:

        artificial_ib_point = rd.language_to_ib_point(
            language=artificial_language,
            prior=uniform_prior,
            meaning_dists=(meaning_dist),
        )
        if use_rkk:
            language_data.append(
                (
                    f"artificial lang {artificial_lang_count}",
                    "artificial",
                    (len(artificial_language.expressions)),
                    artificial_ib_point[1],
                    artificial_ib_point[2],
                )
            )
        else:
            language_data.append(
                (
                    f"artificial lang {artificial_lang_count}",
                    "artificial",
                    math.log(len(artificial_language.expressions)),
                    artificial_ib_point[1],
                    artificial_ib_point[2],
                )
            )

        # Fill in additional color chips
        referents_in_language = []
        for artificial_expression in artificial_language.expressions:
            referents_in_language += artificial_expression.meaning.referents

        # print(f"Artificial language color set size: {len(set(colors_in_language))} colors:{[referent.name for referent in referents_in_language]}")

        # if(GENERATE_ADDITIONAL_COLOR_CHIPS):
        #     for additional_color in color_universe.referents:
        #         if additional_color.name not in colors_in_language:
        #             #Get the closest color to the current color
        #             closest_color_with_term = min([color_term_ref for color_term_ref in color_universe.referents if color_term_ref.name in colors_in_language],
        #                                             key=lambda x: np.linalg.norm(np.array((x.L, x.a, x.b)) - np.array((additional_color.L, additional_color.a, additional_color.b))))
        #             closest_expression = get_expression_from_language(closest_color_with_term.name, artificial_language)
        #             new_refs = list(closest_expression.meaning.referents)+[additional_color]
        #             # Assign the color to the closest expression
        #             closest_expression.meaning= Meaning(tuple(new_refs), universe=color_universe)

    # print(f"Artificial languages{artificial_languages}")

    # Convert the real and artificial languages to DataFrames
    combined_data = pd.DataFrame(
        language_data,
        columns=["name", "type", "complexity", "informativity", "comm_cost"],
    )

    # Convert the Dataframe to a yaml file
    combined_data.to_csv(f"{current_dir}/outputs/complexity_data.csv")

    return combined_data
