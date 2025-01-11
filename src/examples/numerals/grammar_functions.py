from ultk.language.semantics import Referent
from .meaning import universe, addition_table, multiplication_table
from typing import Callable, TypeVar

e = Referent
t = bool
et = Callable[[e], t]
arg = tuple[e]

Number = et
Digit = TypeVar("Digit")
Multiplier = TypeVar("Multiplier")
Phrase = TypeVar("Phrase")

start = t

# Hurford (1975, 2007)
# NUMBER −→ Digit | PHRASE | PHRASE + NUMBER | PHRASE − NUMBER
# PHRASE −→ Multiplier | NUMBER · Multiplier

##############################################################################
# Bind/Apply logic
##############################################################################

# Unwrap args and apply predicate
# t -> Number arg
def apply_et(p: Number, a: arg, name="*") -> t:
    return p(*a)

# Bind args for intermediate node
# arg -> e ...
def bind(*a: e, name=".") -> arg:
    return a

##############################################################################
# Actual grammar
##############################################################################

# NUMBER -> Digit
def _digit(digit: Digit, name="_", weight=5) -> Number:
    return digit

# NUMBER -> PHRASE
def _phrase(phrase: Phrase, name="__") -> Number:
    return phrase


# NUMBER -> PHRASE + NUMBER
def add(phrase: Phrase, number: Number) -> Number:
    return lambda x: any(
        phrase(y) and number(z) and addition_table.get((y.name, z.name)) == x.name
        for y in universe.referents for z in universe.referents
    )

# NUMBER -> PHRASE - NUMBER

# PHRASE -> Multiplier
def mp(multiplier: Multiplier, name="___", weight=10) -> Phrase:
    return multiplier

# PHRASE -> NUMBER * Multiplier
def multiply(number: Number, multiplier: Multiplier) -> Phrase:
    return lambda x: any(
        number(y) and multiplier(z) and multiplication_table.get((y.name, z.name)) == x.name
        for y in universe.referents for z in universe.referents
    )

# Multiplier -> 10
def ten(*_: e) -> Multiplier:
    return lambda x: x.name == 10

# Digit -> 1
def one(*_: e) -> Digit:
    return lambda x: x.name == 1

# Digit -> 2
def two(*_: e) -> Digit:
    return lambda x: x.name == 2

# Digit -> 3

# Digit -> 4

# Digit -> 5

# Digit -> 6

# Digit -> 7

# Digit -> 8

# Digit -> 9

# Digit -> 10
