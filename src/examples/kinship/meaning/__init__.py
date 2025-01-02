from ultk.language.semantics import Referent, Universe
from kinship.meaning.structure import domain


universe = Universe(tuple(Referent(name) for name in domain))
# TODO: add (very nonuniform) prior from KR2012

Ego = Referent("Ego")
