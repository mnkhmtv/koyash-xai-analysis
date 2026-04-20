import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from visualizations import (
    FIGURES_DIR,
    TRIGGERS_PATH,
    plot_age_bias,
)

if __name__ == "__main__":
    triggers_df = pd.DataFrame(json.load(open(TRIGGERS_PATH, encoding="utf-8")))

    os.makedirs(FIGURES_DIR, exist_ok=True)
    plot_age_bias(
        triggers_df,
        save_path=f"{FIGURES_DIR}/figure3_age_bias.png",
    )
