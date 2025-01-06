from ultk.language.semantics import Referent


def _and(a: bool, b: bool) -> bool:
    return a and b


def _or(a: bool, b: bool) -> bool:
    return a or b


def _not(a: bool) -> bool:
    return not a


def _p(w: Referent, name="P") -> bool:
    return w.name == "w1" or w.name == "w2"


def _q(w: Referent, name="Q") -> bool:
    return w.name == "w1" or w.name == "w3"
