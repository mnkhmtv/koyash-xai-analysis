import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from visualizations import (
    FAIRNESS_PATH,
    FIGURES_DIR,
    plot_tone_consistency,
)

if __name__ == "__main__":
    fairness = json.load(open(FAIRNESS_PATH, encoding="utf-8"))

    os.makedirs(FIGURES_DIR, exist_ok=True)
    plot_tone_consistency(
        fairness,
        save_path=f"{FIGURES_DIR}/figure4_tone_consistency.png",
    )
