import pandas as pd
from ultk.language.semantics import Universe

referents = pd.read_csv("connectives/referents.csv")
universe = Universe.from_dataframe(referents)
