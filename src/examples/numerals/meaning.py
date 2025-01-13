import numpy as np
import pandas as pd
from ultk.language.semantics import Universe

df = pd.read_csv("numerals/referents.csv")
numbers = list(df.name)
prior = np.array([n**-2 for n in numbers])
prior /= prior.sum()
df["probability"] = prior
universe = Universe.from_dataframe(df)
