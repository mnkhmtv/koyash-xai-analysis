import pandas as pd
import json
import time
from tqdm import tqdm

from api_client import get_llm_response


INPUT_PATH = "data/generated/counterfactual_prompts_no_dublicates.csv"
OUTPUT_PATH = "data/responses/llm_responses.json"


def run_batch(limit=None):
    df = pd.read_csv(INPUT_PATH)

    if limit:
        df = df.head(limit)

    results = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        pair_id = row["pair_id"]

        original_query = row["original_query"]
        modified_query = row["modified_query"]

        try:
            original_response = get_llm_response(original_query)
            modified_response = get_llm_response(modified_query)

            results.append({
                "pair_id": int(pair_id),
                "change_type": row["change_type"],
                "original_query": original_query,
                "modified_query": modified_query,
                "original_response": original_response,
                "modified_response": modified_response,
            })

            time.sleep(0.5)

        except Exception as e:
            print(f"Error on pair {pair_id}: {e}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(results)} results to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_batch(limit=100)