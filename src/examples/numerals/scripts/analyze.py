import pandas as pd
import plotnine as pn

if __name__ == "__main__":
    combined_data = pd.read_csv("numerals/outputs/combined_data.csv")
    plot = (
        pn.ggplot(pn.aes(
            x="lexicon_size",
            y="avg_morph_complexity",
        ))
        + pn.geom_point(combined_data, pn.aes(color="type"))
        + pn.geom_text(
            combined_data[combined_data["type"] == "natural"],
            pn.aes(label="name"),
            ha="left",
            size=6,
            nudge_x=0.5,
        )
    )
    plot.save("numerals/outputs/plot.png", width=8, height=6, dpi=300)
