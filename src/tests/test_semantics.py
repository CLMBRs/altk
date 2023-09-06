import itertools
import pandas as pd
import pytest
import numpy as np

from ultk.language.semantics import Universe
from ultk.language.semantics import Meaning
from ultk.language.semantics import Referent

forces = ("weak", "strong")
flavors = ("epistemic", "deontic")


class TestSemantics:
    points = [
        {"name": f"{force}+{flavor}", "force": force, "flavor": flavor}
        for (force, flavor) in itertools.product(forces, flavors)
    ]
    dataframe = pd.DataFrame(points)
    universe = Universe.from_dataframe(dataframe)

    ref1 = Referent(
        name="weak+epistemic", properties={"force": "weak", "flavor": "epistemic"}
    )
    ref2 = Referent(
            name="weak+epistemic", properties={"force": "weak", "flavor": "epistemic"}
        )
    ref3 = Referent(
                name="neutral+epistemic",
                properties={"force": "neutral", "flavor": "epistemic"},
            )
    ref4 = Referent(
            name="strong+epistemic", properties={"force": "strong", "flavor": "epistemic"}
        )
    def test_universe_from_df(self):
        assert TestSemantics.points == [
            referent.__dict__ for referent in TestSemantics.universe.referents
        ]

    def test_referent_match(self):
        
        assert TestSemantics.ref1 == TestSemantics.ref2

    def test_referent_mismatch(self):
        
        assert TestSemantics.ref1 != TestSemantics.ref3

    def test_universe_match(self):
        second_dataframe = pd.DataFrame(TestSemantics.points)
        assert Universe.from_dataframe(second_dataframe) == TestSemantics.universe

    def test_universe_mismatch(self):
        ref_list = [TestSemantics.ref1]
        assert Universe(ref_list) != TestSemantics.universe

    def test_meaning_to_array(self):
        test_array = np.array([[0,0],[1,1]])
        meaning_ref = Meaning([TestSemantics.ref1, TestSemantics.ref4], universe=TestSemantics.universe).to_array()
        print(meaning_ref)
        assert not (meaning_ref - test_array).any()

    def test_meaning_subset(self):
        ref_list = [TestSemantics.ref1]
        meaning = Meaning(
            ref_list, TestSemantics.universe
        )  # This meaning should exist within the set of semantics
        assert TestSemantics.ref1 in meaning.referents

        with pytest.raises(ValueError):
            ref_list.append(
                Referent(
                    name="neutral+epistemic",
                    properties={"force": "neutral", "flavor": "epistemic"},
                )
            )
            meaning = Meaning(
                ref_list, TestSemantics.universe
            )  
