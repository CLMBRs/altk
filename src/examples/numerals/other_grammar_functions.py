from ultk.language.semantics import Referent
from .meaning import universe, addition_table, multiplication_table
from typing import Callable, TypeVar

# All ints, as far as i can tell
Number = TypeVar("Number")
Digit = TypeVar("Digit")
Multiplier = TypeVar("Multiplier")
Phrase = TypeVar("Phrase")

start = Number

# Hurford (1975, 2007)
# NUMBER −→ Digit | PHRASE | PHRASE + NUMBER | PHRASE − NUMBER
# PHRASE −→ Multiplier | NUMBER · Multiplier



# NUMBER -> PHRASE + NUMBER
def add(p: Phrase, n: Number) -> Number:
    return p + n

# NUMBER -> PHRASE
def phrase(p: Phrase) -> Number:
    return p


# NUMBER -> Digit
def digit(d: Digit) -> Number:
    return d


# PHRASE -> NUMBER * Multiplier
def multiply(n: Number, m: Multiplier) -> Phrase:
    return n * m

# PHRASE -> Multiplier
def multiplier(m: Multiplier) -> Phrase:
    return m

# Terminal Rules

# Multiplier -> referent
def multiplier_terminal(x: Referent,) -> Multiplier:
    return x.name

# Digit -> referent
def digit_terminal(x: Referent,) -> Digit:
    return x.name

