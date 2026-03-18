import json
import pandas as pd

from recommendation_parser import extract_products
from price_extractor import extract_prices
from sentiment_analyzer import detect_tone


INPUT_PATH = "data/responses/llm_responses.json"
OUTPUT_PATH = "data/processed/analysis_dataset.csv"


def parse():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for item in data:
        pair_id = item["pair_id"]

        orig_text = item["original_response"]
        orig_products = extract_products(orig_text)
        orig_prices = extract_prices(orig_text)

        mod_text = item["modified_response"]
        mod_products = extract_products(mod_text)
        mod_prices = extract_prices(mod_text)

        rows.append({
            "pair_id": pair_id,
            "change_type": item["change_type"],

            "original_products": orig_products,
            "modified_products": mod_products,

            "original_prices": orig_prices,
            "modified_prices": mod_prices,

            "original_tone": detect_tone(orig_text),
            "modified_tone": detect_tone(mod_text),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved parsed dataset to {OUTPUT_PATH}")


if __name__ == "__main__":
    parse()