from ultk.language.semantics import Referent
from typing import TypeVar


Number = TypeVar("Number")
Digit = Referent
Phrase = TypeVar("Phrase")
Multiplier = TypeVar("Multiplier")

arg = tuple[Referent]
start = bool


# Unwrap args and apply predicate
# t -> Number arg
def apply_et(n: Number, a: arg, name="*") -> bool:
    return n == a[0].name


# Bind args for intermediate node
# arg -> e ...
def bind(*a: Referent, name=".") -> arg:
    return a


# Hurford (1975, 2007)
# NUMBER −→ Digit | PHRASE | PHRASE + NUMBER | PHRASE − NUMBER
# PHRASE −→ Multiplier | NUMBER · Multiplier


# NUMBER -> PHRASE + NUMBER
def add(p: Phrase, n: Number) -> Number:
    return p + n


# NUMBER -> PHRASE - NUMBER
def sub(p: Phrase, n: Number) -> Number:
    return p - n


# NUMBER -> PHRASE
def phrase(p: Phrase, name=" ") -> Number:
    return p


# NUMBER -> Digit

# language-specific digit terms omitted, e.g.,
# def one(_: Digit) -> Number:
# return 1


# PHRASE -> NUMBER * Multiplier
# PHRASE -> Multiplier


# PHRASE -> NUMBER * Multiplier
def multiply(n: Number, m: Multiplier) -> Phrase:
    return n * m


# language-specific multipliers omitted, e.g.,
# def _ten(_: Referent) -> Multiplier:
# return 10
