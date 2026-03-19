import pandas as pd
import json
import ast
import os

df = pd.read_csv("data/processed/analysis_dataset.csv")

triggers = []

for _, row in df.iterrows():
    try:
        original_products = set(ast.literal_eval(row["original_products"]))
        modified_products = set(ast.literal_eval(row["modified_products"]))
    except:
        continue

    product_changed = original_products != modified_products

    try:
        orig_prices = ast.literal_eval(row["original_prices"])
        mod_prices = ast.literal_eval(row["modified_prices"])
        orig_prices = [float(p) for p in orig_prices if p]
        mod_prices = [float(p) for p in mod_prices if p]
        avg_orig = sum(orig_prices) / len(orig_prices) if orig_prices else 0
        avg_mod = sum(mod_prices) / len(mod_prices) if mod_prices else 0
        price_diff = round(avg_mod - avg_orig, 2)
    except:
        price_diff = None

    triggers.append({
        "pair_id": int(row["pair_id"]),
        "change_type": row["change_type"],
        "product_changed": product_changed,
        "products_removed": list(original_products - modified_products),
        "products_added": list(modified_products - original_products),
        "price_diff": price_diff
    })

os.makedirs("data/processed", exist_ok=True)
with open("data/processed/triggers.json", "w", encoding="utf-8") as f:
    json.dump(triggers, f, indent=2, ensure_ascii=False)

total = len(triggers)
changed = sum(1 for t in triggers if t["product_changed"])
print(f"✅ Processed {total} pairs")
print(f"📦 Product changed: {changed}/{total} ({round(changed/total*100)}%)")
print(f"💾 Saved to data/processed/triggers.json")  