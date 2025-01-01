# Following Kemp and Regier 2012, the objects in the domain are relatives of the speaker (Ego). 
# This is also convenient because the GrammaticalExpression.func takes a single Referent as input,
# suggesting that a Referent should be a relative encoded as pair of (Ego, other).

from ultk.language.semantics import Referent, Universe
from kinship.structure import domain


universe = Universe(
    tuple(
        Referent(name)
        for name in domain
    )
)
Ego = Referent("Ego")