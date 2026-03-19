import pandas as pd
import json
import os
import ast

df = pd.read_csv("data/processed/analysis_dataset.csv")
triggers = json.load(open("data/processed/triggers.json"))
triggers_df = pd.DataFrame(triggers)

merged = df.merge(triggers_df, on=["pair_id", "change_type"])

# 1. Product change rate
product_change_rate = merged["product_changed"].mean()

# 2. Average price diff overall
avg_price_diff = merged["price_diff"].dropna().mean()

# 3. Price bias by change_type
price_bias_by_type = (
    merged.groupby("change_type")["price_diff"]
    .mean()
    .dropna()
    .to_dict()
)

# 4. Tone consistency по change_type
tone_changed = []
for _, row in merged.iterrows():
    try:
        orig_tone = str(row["original_tone"]).strip().lower()
        mod_tone = str(row["modified_tone"]).strip().lower()
        tone_changed.append(orig_tone != mod_tone)
    except:
        tone_changed.append(None)

merged["tone_changed"] = tone_changed

tone_consistency = (
    merged.groupby("change_type")["tone_changed"]
    .apply(lambda x: 1 - x.dropna().mean())
    .to_dict()
)

report = {
    "product_change_rate": round(product_change_rate, 4),
    "avg_price_diff": round(avg_price_diff, 4),
    "price_bias_by_change_type": {
        k: round(v, 4) for k, v in price_bias_by_type.items()
    },
    "tone_consistency_by_change_type": {
        k: round(v, 4) for k, v in tone_consistency.items()
    }
}

with open("data/results/fairness_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("✅ Fairness report saved!")
print(json.dumps(report, indent=2))