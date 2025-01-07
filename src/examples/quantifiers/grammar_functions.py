# Grammar from https://github.com/CLMBRs/ultk/blob/9e6ef27e56f466e5edca630ee3f291bee02164c6/src/examples/learn_quant/grammar.yml

from ultk.language.semantics import Referent


def _and(a: bool, b: bool, name="and", weight=1.0) -> bool:
    return a and b


def _or(a: bool, b: bool, name="or", weight=1.0) -> bool:
    return a or b


def _not(a: bool, name="not", weight=1.0) -> bool:
    return not a

# Set logic rules
def _union(s1: frozenset, s2: frozenset, name="union", weight=1.0) -> frozenset:
    return s1 | s2

def _intersection(s1: frozenset, s2: frozenset, name="intersection", weight=1.0) -> frozenset:
    return s1 & s2

def _difference(s1: frozenset, s2: frozenset, name="difference", weight=1.0) -> frozenset:
    return s1 - s2

def _index(i: int, s: frozenset, name="index", weight=1.0) -> frozenset:
    return frozenset([sorted(s)[i]]) if i < len(s) else frozenset()

def _cardinality(s: frozenset, name="cardinality", weight=1.0) -> int:
    return len(s)

def _subset_eq(s1: frozenset, s2: frozenset, name="subset_eq", weight=1.0) -> bool:
    return s1 <= s2

# Integer logical rules
def _equals(i1: int, i2: int, name="equals", weight=1.0) -> bool:
    return i1 == i2

def _greater_than(i1: int, i2: int, name="greater_than", weight=1.0) -> bool:
    return i1 > i2

# Primitive rules
def _A(q: Referent, name="A", weight=10.0) -> frozenset:
    return q.A

def _B(q: Referent, name="B", weight=10.0) -> frozenset:
    return q.B