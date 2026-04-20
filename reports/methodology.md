# 3. Methodology and Implementation

## 3.1 Dataset Construction

To systematically investigate bias in LLM-generated skincare recommendations, we constructed a dataset of **counterfactual prompt pairs**. Each pair consists of two prompts that are identical in structure and skincare-related content, differing only in a single demographic or contextual variable. This counterfactual design allows us to isolate the effect of each variable on the model's output.

We defined six **change types**, representing the dimensions along which prompts were varied:

| Change Type | Description |
|---|---|
| `age_change` | User's stated age is modified (e.g., 20 → 45) |
| `skin_type_change` | Skin type is changed (e.g., oily → dry) |
| `concern_change` | Primary skin concern is altered (e.g., acne → wrinkles) |
| `budget_change` | Budget constraint is shifted (e.g., $30 → $100) |
| `ingredient_pref_change` | Preferred ingredients are swapped (e.g., retinol → niacinamide) |
| `ingredient_avoid_change` | Avoided ingredients are changed (e.g., fragrance → alcohol) |

Base prompt templates were stored in `data/raw/base_prompts.csv`. The `demographic_variator.py` module systematically applied each variation to produce the final set of **75 counterfactual pairs** (`data/generated/counterfactual_prompts_no_duplicates.csv`), with duplicates removed to ensure dataset integrity.

## 3.2 LLM Interaction

All prompt pairs were sent to a large language model via API using the `batch_api_caller.py` module. The system instruction framed the model as a professional skincare advisor. For each pair, both the original and the modified prompt were submitted independently in separate API calls to prevent cross-contamination between responses.

Raw responses were stored in `data/responses/llm_responses.json` as a list of records, each containing:
- `pair_id` — unique identifier linking the two prompts
- `change_type` — the dimension varied in this pair
- `original_response` — LLM output for the baseline prompt
- `modified_response` — LLM output for the modified prompt

API key management followed best practices: credentials were loaded exclusively from environment variables via a `.env` file (see `.env.example`), and no keys were hardcoded in source files.

## 3.3 Response Parsing

Raw LLM responses were processed through a three-stage parsing pipeline implemented in `parse_responses.py`:

**Product extraction** (`recommendation_parser.py`): A regex- and heuristic-based extractor identified product names mentioned in each response, leveraging patterns common to skincare brand and product naming conventions.

**Price extraction** (`price_extractor.py`): Dollar-amount patterns were extracted from the response text using regular expressions. Multiple prices within a single response were collected as a list, and the per-response mean price was computed for downstream analysis.

**Tone detection** (`sentiment_analyzer.py`): Each response was assigned a tone label (e.g., *neutral*, *positive*, *cautious*) using a rule-based sentiment classifier. Tone consistency between the original and modified responses was then used as a proxy for stylistic bias.

Parsed results were saved to `data/processed/analysis_dataset.csv`, with one row per prompt pair containing original and modified products, prices, and tones.

## 3.4 Bias Metrics

Trigger detection (`trigger_detector.py`) compared the original and modified product sets for each pair, recording which products were added or removed and computing the average price difference:

$$\Delta p_i = \bar{p}^{\text{mod}}_i - \bar{p}^{\text{orig}}_i$$

where $\bar{p}$ denotes the mean price of the recommended products in a given response.

The fairness report (`fairness_metrics.py`) aggregated the following metrics across the full dataset and per change type:

- **Product Change Rate** — fraction of pairs in which the set of recommended products changed:

$$\text{PCR} = \frac{1}{N} \sum_{i=1}^{N} \mathbf{1}[\mathcal{P}^{\text{orig}}_i \neq \mathcal{P}^{\text{mod}}_i]$$

- **Average Price Difference** — mean $\Delta p_i$ per change type, indicating systematic up- or down-pricing across demographic groups.

- **Tone Consistency** — fraction of pairs where the tone label was identical between original and modified responses, measuring stylistic stability:

$$\text{TC} = \frac{1}{N} \sum_{i=1}^{N} \mathbf{1}[\tau^{\text{orig}}_i = \tau^{\text{mod}}_i]$$

## 3.5 Pipeline Pseudocode

The complete analysis pipeline is summarised below. A detailed version with per-module pseudocode is provided in Appendix A.

```
INPUT: base_prompts.csv

1. GENERATE counterfactual pairs
   FOR each base_prompt IN base_prompts:
     FOR each change_type IN [age, skin_type, concern, budget, ingr_pref, ingr_avoid]:
       pair = apply_variation(base_prompt, change_type)
       pairs.append(pair)
   DEDUPLICATE pairs → save to counterfactual_prompts.csv

2. QUERY LLM
   FOR each pair IN pairs:
     original_response  = llm_api(pair.original_prompt)
     modified_response  = llm_api(pair.modified_prompt)
   SAVE responses → llm_responses.json

3. PARSE responses
   FOR each response_record IN llm_responses:
     products = extract_products(response_record)
     prices   = extract_prices(response_record)
     tone     = detect_tone(response_record)
   SAVE → analysis_dataset.csv

4. DETECT triggers
   FOR each pair IN analysis_dataset:
     product_changed = (original_products ≠ modified_products)
     price_diff      = mean(modified_prices) − mean(original_prices)
   SAVE → triggers.json

5. COMPUTE fairness metrics
   product_change_rate     = mean(product_changed)
   avg_price_diff          = mean(price_diff)  [per change_type]
   tone_consistency        = mean(original_tone == modified_tone)  [per change_type]
   SAVE → fairness_report.json

6. VISUALISE results (see Figures 1–5)
```

The visualisation step produces five figures described in Section 4, generated via `src/visualization/visualizations.py`. Figure 2 presents the trigger heatmap summarising all three metrics across change types. Figure 3 focuses on price bias with age change highlighted. Figure 5 shows the correlation between original and modified prices at the pair level.