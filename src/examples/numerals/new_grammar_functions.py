from ultk.language.semantics import Referent
from .meaning import universe, addition_table, multiplication_table
from typing import Callable, TypeVar

# All ints, as far as i can tell; 
# but then final meaning is int, i.e. all true-like
# so we'll need to interpret the meaning in a special way

Number = TypeVar("Number")
Digit = Referent
Multiplier = Referent
Phrase = TypeVar("Phrase")


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
# def add(p: Phrase, n: Number) -> Number:
#     return p + n

# NUMBER -> PHRASE - NUMBER
def sub(p: Phrase, n: Number) -> Number:
    return p - n

# NUMBER -> PHRASE
def phrase(p: Phrase, name=" ") -> Number:
    return p


# NUMBER -> Digit

def one(_: Digit) -> Number:
    return 1

def two(_: Digit) -> Number:
    return 2

def three(_: Digit) -> Number:
    return 3

def four(_: Digit) -> Number:
    return 4

def five(_: Digit) -> Number:
    return 5

def six(_: Digit) -> Number:
    return 6

def seven(_: Digit) -> Number:
    return 7

def eight(_: Digit) -> Number:
    return 8

def nine(_: Digit) -> Number:
    return 9

def ten(_: Digit) -> Number:
    return 10


# PHRASE -> NUMBER * Multiplier
# PHRASE -> Multiplier
# This can be simplified to one multiplication rule per Multiplier
def multiply_ten(n: Number, name="x10") -> Phrase:
    return n * 10

def multiply_twenty(n: Number, name="x20") -> Phrase:
    return n * 20