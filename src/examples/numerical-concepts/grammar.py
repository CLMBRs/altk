from universe import NumberReferent

# BOOLEAN OPERATORS


def _and(a: bool, b: bool) -> bool:
    return a and b


def _or(a: bool, b: bool) -> bool:
    return a or b


def _not(a: bool) -> bool:
    return not a


def _equals(num1: float, num2: float) -> bool:
    return num1 == num2


def _less_than(num1: float, num2: float) -> bool:
    return num1 < num2


# NUMERICAL OPERATORS


def _times(num1: float, num2: float) -> float:
    return num1 * num2


def _plus(num1: float, num2: float) -> float:
    return num1 + num2


# PRIMITIVES


def proj1(pair: NumberReferent) -> float:
    return pair.first_number


def proj2(pair: NumberReferent) -> float:
    return pair.second_number
