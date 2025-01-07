import math
from ..meaning import QuantifierModel

start = bool

# Boolean operations

# bool -> bool bool
def _and(p: bool, q: bool, name="and") -> bool:
    return p and q

def _or(p: bool, q: bool, name="or") -> bool:
    return p or q

# bool -> bool
def _not(p: bool, name="not") -> bool:
    return not p

# Set operations

# bool -> frozenset frozenset
def intersection(a: frozenset, b: frozenset) -> bool:
    return a & b

def union(a: frozenset, b: frozenset) -> bool:
    return a | b

def subset(a: frozenset, b: frozenset) -> bool:
    return a < b

# int -> frozenset
def cardinality(a: frozenset) -> int:
    return len(a)

# Numeric operations

# float -> int int
def divide(x: int, y: int, name="/") -> float:
    return x / y if y > 0 else 0

# int -> int int
def plus(x: int, y: int, name="+") -> int:
    return x + y

def minus(x: int, y: int, name="-") -> int:
    return x - y

# bool -> int int
def gt(x: int, y: int, name=">") -> bool:
    return x > y

def eq(x: int, y: int, name="=") -> bool:
    return x == y

def mod(x: int, y: int, name="%") -> bool:
    return x % y if y > 0 else 0

# bool -> float float
def eqf(x: float, y: float, name="=f") -> bool:
    return math.isclose(x, y)

def gtf(x: float, y: float, name=">f") -> bool:
    return x > y

# Primitives

# frozenset -> model
def _A(model: QuantifierModel, name="A") -> frozenset:
    return model.A

def _A(model: QuantifierModel, name="B") -> frozenset:
    return model.B
