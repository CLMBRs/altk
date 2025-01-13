from ultk.language.semantics import Referent

from .base_grammar import Number, Phrase, Digit, Multiplier

# All ints, as far as i can tell; 
# but then final meaning is int, i.e. all true-like
# so we'll need to interpret the meaning in a special way

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
# def sub(p: Phrase, n: Number) -> Number:
#     return p - n

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
# This could be simplified to one multiplication rule per Multiplier, 
# but for bookkeeping we'll separate them out
# def multiply_ten(n: Number, name="x10") -> Phrase:
    # return n * 10

# PHRASE -> NUMBER * Multiplier
def multiply(n: Number, m: Multiplier) -> Phrase:
    return n * m

# Multiplier -> ' ', because its important Multiplier is not a Referent
def _ten(_: Referent) -> Multiplier:
    return 10