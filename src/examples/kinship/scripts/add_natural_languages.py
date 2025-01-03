import pandas as pd
from ..data.english_system import english_system
from ..meaning import sorted_names


if __name__ == "__main__":
    # Convert to a DataFrame
    df = pd.DataFrame(columns=["language", "expression"] + sorted_names)

    # For now, just add English
    for term, referents in english_system.items():
        row = {referent: (referent in referents) for referent in sorted_names}
        row["language"] = "English"
        row["expression"] = term
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    fn = "kinship/data/natural_languages.csv"
    df.to_csv(fn, index=False)
    print(f"Wrote to {fn}.")
