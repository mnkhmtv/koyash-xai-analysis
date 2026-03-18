import json
import pandas as pd


INPUT_PATH = "data/results/triggers.json"
OUTPUT_PATH = "data/results/fairness_report.json"


def compute_metrics():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    product_change_rate = df["product_changed"].mean()
    avg_price_diff = df["price_diff"].mean()

    price_bias_by_type = (
        df.groupby("change_type")["price_diff"]
        .mean()
        .to_dict()
    )

    result = {
        "product_change_rate": product_change_rate,
        "avg_price_diff": avg_price_diff,
        "price_bias_by_change_type": price_bias_by_type,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("Fairness report saved")


if __name__ == "__main__":
    compute_metrics()