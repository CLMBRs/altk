from ultk.language.semantics import Referent, Universe
from .structure import domain
from ..data.prior_weights import weights

import numpy as np

sorted_names = sorted(domain)
sorted_weights = np.array([weights[name] for name in sorted_names])
prior = sorted_weights / sorted_weights.sum()

universe = Universe(
    tuple(Referent(name) for name in sorted_names),
    tuple(prior),
)

Ego = Referent("Ego")
