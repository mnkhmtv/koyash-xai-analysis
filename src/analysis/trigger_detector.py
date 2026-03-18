import pandas as pd
import ast
import json


INPUT_PATH = "data/processed/analysis_dataset.csv"
OUTPUT_PATH = "data/results/triggers.json"


def detect_triggers():
    df = pd.read_csv(INPUT_PATH)

    results = []

    for _, row in df.iterrows():
        pair_id = row["pair_id"]
        change_type = row["change_type"]

        orig_products = ast.literal_eval(row["original_products"])
        mod_products = ast.literal_eval(row["modified_products"])

        orig_prices = ast.literal_eval(row["original_prices"])
        mod_prices = ast.literal_eval(row["modified_prices"])

        product_changed = orig_products != mod_products

        if orig_prices and mod_prices:
            avg_orig = sum(orig_prices) / len(orig_prices)
            avg_mod = sum(mod_prices) / len(mod_prices)
            price_diff = avg_mod - avg_orig
        else:
            price_diff = None

        results.append({
            "pair_id": int(pair_id),
            "change_type": change_type,
            "product_changed": product_changed,
            "price_diff": price_diff,
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Saved triggers to {OUTPUT_PATH}")


if __name__ == "__main__":
    detect_triggers()