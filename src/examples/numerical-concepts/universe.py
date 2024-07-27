from ultk.language.semantics import Universe, Referent


class NumberReferent(Referent):
    def __init__(self, first_number: float, second_number: float):
        super().__init__(
            name=f"NumberReferent: ({first_number} , {second_number})",
            properties={"first_number": first_number, "second_number": second_number},
        )


MAX_NUM = 10
referents = tuple(
    NumberReferent(num1, num2) for num1 in range(MAX_NUM) for num2 in range(MAX_NUM)
)
number_universe = Universe(referents, tuple(1 / len(referents) for _ in referents))
