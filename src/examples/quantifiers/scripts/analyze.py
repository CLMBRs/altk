import pandas as pd
import plotnine as pn
from scipy.stats import pearsonr

if __name__ == "__main__":
    combined_data = pd.read_csv("quantifiers/outputs/combined_data.csv")
    corr_str = f"$\\rho=${pearsonr(combined_data.naturalness, combined_data.optimality).correlation:.3f}"
    plot = (
        pn.ggplot(pn.aes(x="complexity", y="comm_cost"))
        + pn.geom_point(
            combined_data[combined_data["type"] == "dominant"], color="black", size=3
        )        
        + pn.geom_point(combined_data, pn.aes(color="naturalness"))
        + pn.scale_color_continuous("cividis")
        + pn.geom_label(
            pd.DataFrame(
                [list(combined_data[["complexity", "comm_cost"]].mean()) + [corr_str]],
                columns=["complexity", "comm_cost", "label"],
            ),
            pn.aes(label="label"),
        )
    )
    plot.save("quantifiers/outputs/plot.png", width=8, height=6, dpi=300)
