import itertools
import pandas as pd
import pytest

from ultk.language.language import Expression, Language
from ultk.language.semantics import Referent, Universe, Meaning


class TestLanguage:
    pairs = {
        "shroom": "fungus",
        "dog": "animal",
        "tree": "plant",
        "cat": "animal",
        "bird": "animal",
    }
    pairs2 = {"shroom": "fungus", "dog": "animal", "tree": "plant", "bird": "bird"}

    uni_refs = [Referent(key, {"phylum": val}) for (key, val) in pairs.items()]
    uni = Universe(uni_refs)
    uni2 = Universe([Referent(key, {"phylum": val}) for (key, val) in pairs2.items()])

    meaning = Meaning(referents=uni_refs, universe=uni)
    exp = Expression(
        form="dog",
        meaning=Meaning(
            referents=[Referent("dog", {"phylum": "animal"})], universe=uni
        ),
    )
    exp2 = Expression(
        form="cat",
        meaning=Meaning(
            referents=[Referent("cat", {"phylum": "animal"})], universe=uni
        ),
    )
    exp3 = Expression(
        form="tree",
        meaning=Meaning(
            referents=[Referent("tree", {"phylum": "plant"})], universe=uni
        ),
    )
    exp4 = Expression(
        form="shroom",
        meaning=Meaning(
            referents=[Referent("shroom", {"phylum": "fungus"})], universe=uni
        ),
    )
    exp5 = Expression(
        form="bird",
        meaning=Meaning(
            referents=[Referent("bird", {"phylum": "animal"})], universe=uni
        ),
    )

    lang = Language(expressions=[exp, exp2, exp3, exp4])
    lang2 = Language(expressions=[exp, exp2, exp3, exp5])
    lang3 = Language(expressions=[exp, exp2, exp3])
    lang4 = Language(expressions=[exp, exp2, exp4, exp3])

    def test_exp_subset(self):
        assert TestLanguage.exp.can_express(Referent("dog", {"phylum": "animal"}))

    def test_exp_not_subset(self):
        assert not TestLanguage.exp.can_express(Referent("cat", {"phylum": "animal"}))

    def test_language_has_expressions(self):
        with pytest.raises(ValueError):
            lang2 = Language([])

    def test_language_universe_check(self):
        with pytest.raises(ValueError):
            lang2 = Language(
                [
                    TestLanguage.exp,
                    Expression(
                        form="dog",
                        meaning=Meaning(
                            referents=[Referent("dog", {"phylum": "animal"})],
                            universe=TestLanguage.uni2,
                        ),
                    ),
                ]
            )

    def test_language_degree(self):
        def isAnimal(exp: Expression) -> bool:
            print("checking phylum of " + str(exp.meaning.referents[0]))
            return exp.meaning.referents[0].to_dict()["phylum"] == "animal"

        assert TestLanguage.lang.degree_property(isAnimal) == 0.5

    def test_language_len(self):
        assert TestLanguage.lang.__len__() == 4

    def test_language_equality(self):
        assert TestLanguage.lang != TestLanguage.lang2
        assert TestLanguage.lang != TestLanguage.lang3
        assert TestLanguage.lang == TestLanguage.lang4
