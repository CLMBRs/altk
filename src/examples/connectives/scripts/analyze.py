import pandas as pd
import plotnine as pn

if __name__ == "__main__":
    combined_data = pd.read_csv("connectives/outputs/combined_data.csv")
    plot = (
        pn.ggplot(pn.aes(x="complexity", y="comm_cost"))
        + pn.geom_point(
            combined_data[combined_data["type"] == "dominant"], color="black", size=6
        )
        + pn.geom_point(
            combined_data,
            pn.aes(fill="commutative"),
            size=4,
        )
        + pn.scale_fill_manual(values=["#3c8dbc", "#ff7f0e"])
        + pn.geom_point(
            combined_data[combined_data["commutative"]], fill="#ff7f0e", size=4
        )
    )
    plot.save("connectives/outputs/plot.png", width=8, height=6, dpi=300)
