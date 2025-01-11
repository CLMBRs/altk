import pandas as pd
from ultk.language.semantics import Universe, Referent
from typing import Callable

universe = Universe.from_csv("numerals/referents.csv")

def create_table(referents: tuple[Referent], func: Callable[[int, int], int]) -> dict[tuple[int, int], int]:
    return {(x.name, y.name): func(x.name, y.name) for x in referents for y in referents}

# precompute tables for faster search
addition_table = create_table(universe.referents, lambda x,y: x+y)
multiplication_table = create_table(universe.referents, lambda x,y: x*y)
