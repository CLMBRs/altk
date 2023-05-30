from altk.language.semantics import Referent
from itertools import chain, combinations

import random


class QuantifierBaseModel(Referent):
    _M = {}
    powerset = []

    def __init__(self, m, name, **kwargs):
        super().__init__(name, **kwargs)
        self._M = m
        self.powerset = list(chain.from_iterable(combinations(self._M, r)
                                                 for r in range(len(self._M) + 1)))

        self._A = random.choice(self.powerset)
        self._B = random.choice(self.powerset)


    @property
    def M(self):
        return self._M

    @M.setter
    def M(self, value):
        self._M = value

    @M.deleter
    def M(self):
        del self._M

    @property
    def A(self):
        return self._A

    @A.setter
    def A(self, value):
        self._A = value

    @A.deleter
    def A(self):
        del self._A

    @property
    def B(self):
        return self._B

    @B.setter
    def B(self, value):
        self._B = value

    @B.deleter
    def B(self):
        del self._B

    def display(self):
        print(self._M)
        print(self._A)
        print(self._B)
