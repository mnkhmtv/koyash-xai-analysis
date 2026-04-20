import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from visualizations import (
    DATASET_PATH,
    FIGURES_DIR,
    TRIGGERS_PATH,
    plot_trigger_heatmap,
)

if __name__ == "__main__":
    df = pd.read_csv(DATASET_PATH)
    triggers_df = pd.DataFrame(json.load(open(TRIGGERS_PATH, encoding="utf-8")))

    os.makedirs(FIGURES_DIR, exist_ok=True)
    plot_trigger_heatmap(
        df,
        triggers_df,
        save_path=f"{FIGURES_DIR}/figure2_trigger_heatmap.png",
    )
