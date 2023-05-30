import pandas as pd
from altk.language.semantics import Universe

referents = pd.read_csv("quantifiers/referents.csv")
#TODO: neeed to generate the data for use and convert to a dataframe then use from df function in referents library
# prior = pd.read_csv("quantifiers/data/TODO.csv")
# assert (referents["name"] == prior["name"]).all()
# referents["probability"] = prior["probability"]
universe = Universe.from_dataframe(referents)
