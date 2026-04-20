# Appendix A: Code and Pseudocode

This appendix provides pseudocode for each major module in the Koyash-XAI pipeline. The pseudocode is written in a language-agnostic style to aid reproducibility and clarity. Full source code is available in the project repository.

---

## A.1 Pipeline Overview

The end-to-end pipeline processes base prompt templates through five sequential stages and produces a fairness report alongside five visualisation figures.

```
PROCEDURE run_full_pipeline():

  pairs    ← generate_counterfactual_pairs("data/raw/base_prompts.csv")
  responses ← query_llm_batch(pairs)
  dataset  ← parse_responses(responses)
  triggers ← detect_triggers(dataset)
  report   ← compute_fairness_metrics(dataset, triggers)
  figures  ← generate_visualisations(dataset, triggers, report)

  SAVE report   → "data/results/fairness_report.json"
  SAVE figures  → "reports/figures/"

END PROCEDURE
```

---

## A.2 Counterfactual Pair Generation

```
PROCEDURE generate_counterfactual_pairs(base_prompts_path):

  base_prompts ← load_csv(base_prompts_path)
  pairs        ← empty list

  CHANGE_TYPES ← [age_change, skin_type_change, concern_change,
                  budget_change, ingredient_pref_change, ingredient_avoid_change]

  FOR each template IN base_prompts:
    FOR each change_type IN CHANGE_TYPES:

      original_prompt ← fill_template(template, profile="baseline")
      modified_prompt ← fill_template(template, profile=vary(change_type))

      pair ← {
        pair_id:        generate_id(),
        change_type:    change_type,
        original_prompt: original_prompt,
        modified_prompt: modified_prompt
      }
      pairs.append(pair)

  pairs ← deduplicate(pairs)
  SAVE pairs → "data/generated/counterfactual_prompts_no_duplicates.csv"
  RETURN pairs

END PROCEDURE


PROCEDURE vary(change_type):
  // Returns a modified user profile for the given change dimension
  IF change_type == age_change:        RETURN swap_age()
  IF change_type == skin_type_change:  RETURN swap_skin_type()
  IF change_type == concern_change:    RETURN swap_concern()
  IF change_type == budget_change:     RETURN swap_budget()
  IF change_type == ingredient_pref_change:  RETURN swap_preferred_ingredient()
  IF change_type == ingredient_avoid_change: RETURN swap_avoided_ingredient()
END PROCEDURE
```

---

## A.3 LLM Batch Query

```
PROCEDURE query_llm_batch(pairs):

  responses ← empty list
  api_client ← initialise_llm_client(api_key=ENV["OPENAI_API_KEY"])

  FOR each pair IN pairs:

    original_response ← api_client.complete(
      system = "You are a professional skincare advisor.",
      user   = pair.original_prompt
    )

    modified_response ← api_client.complete(
      system = "You are a professional skincare advisor.",
      user   = pair.modified_prompt
    )

    responses.append({
      pair_id:           pair.pair_id,
      change_type:       pair.change_type,
      original_response: original_response,
      modified_response: modified_response
    })

  SAVE responses → "data/responses/llm_responses.json"
  RETURN responses

END PROCEDURE
```

---

## A.4 Response Parsing

```
PROCEDURE parse_responses(responses):

  rows ← empty list

  FOR each record IN responses:

    // --- product extraction ---
    orig_products ← extract_products(record.original_response)
    mod_products  ← extract_products(record.modified_response)

    // --- price extraction ---
    orig_prices ← extract_prices(record.original_response)   // returns list of floats
    mod_prices  ← extract_prices(record.modified_response)

    // --- tone detection ---
    orig_tone ← detect_tone(record.original_response)        // e.g. "neutral"
    mod_tone  ← detect_tone(record.modified_response)

    rows.append({
      pair_id:           record.pair_id,
      change_type:       record.change_type,
      original_products: orig_products,
      modified_products: mod_products,
      original_prices:   orig_prices,
      modified_prices:   mod_prices,
      original_tone:     orig_tone,
      modified_tone:     mod_tone
    })

  dataset ← DataFrame(rows)
  SAVE dataset → "data/processed/analysis_dataset.csv"
  RETURN dataset

END PROCEDURE


PROCEDURE extract_products(text):
  // Regex + heuristic scan for known brand/product name patterns
  candidates ← regex_findall(PRODUCT_PATTERN, text)
  RETURN deduplicate(candidates)

PROCEDURE extract_prices(text):
  // Match dollar amounts, e.g. "$19.99" or "19 dollars"
  raw_matches ← regex_findall(PRICE_PATTERN, text)
  RETURN [to_float(m) FOR m IN raw_matches]

PROCEDURE detect_tone(text):
  // Rule-based classifier: count positive / negative / neutral signal words
  score ← sentiment_score(text)
  IF score > THRESHOLD_POS:  RETURN "positive"
  IF score < THRESHOLD_NEG:  RETURN "negative"
  RETURN "neutral"
```

---

## A.5 Bias Metric Computation

```
PROCEDURE detect_triggers(dataset):

  triggers ← empty list

  FOR each row IN dataset:
    orig_set ← set(row.original_products)
    mod_set  ← set(row.modified_products)

    product_changed  ← (orig_set ≠ mod_set)
    products_removed ← orig_set − mod_set
    products_added   ← mod_set − orig_set

    avg_orig ← mean(row.original_prices)  // 0 if list is empty
    avg_mod  ← mean(row.modified_prices)
    price_diff ← avg_mod − avg_orig

    triggers.append({
      pair_id:          row.pair_id,
      change_type:      row.change_type,
      product_changed:  product_changed,
      products_removed: products_removed,
      products_added:   products_added,
      price_diff:       price_diff
    })

  SAVE triggers → "data/processed/triggers.json"
  RETURN triggers

END PROCEDURE


PROCEDURE compute_fairness_metrics(dataset, triggers):

  merged ← join(dataset, triggers, on=pair_id)

  product_change_rate ← mean(merged.product_changed)
  avg_price_diff      ← mean(merged.price_diff)

  // Per change_type breakdowns
  FOR each change_type IN unique(merged.change_type):
    subset ← filter(merged, change_type)
    price_bias[change_type]      ← mean(subset.price_diff)
    tone_consistency[change_type] ← mean(subset.original_tone == subset.modified_tone)

  report ← {
    product_change_rate:          product_change_rate,
    avg_price_diff:               avg_price_diff,
    price_bias_by_change_type:    price_bias,
    tone_consistency_by_change_type: tone_consistency
  }

  SAVE report → "data/results/fairness_report.json"
  RETURN report

END PROCEDURE
```

---

## A.6 Reproducibility

To reproduce all results from scratch:

```
# 1. Install dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Set up API credentials
cp .env.example .env
# → add your OPENAI_API_KEY to .env

# 3. Run pipeline steps in order
python src/generation/prompt_generator.py
python src/llm/batch_api_caller.py
python src/analysis/parse_responses.py
python src/analysis/trigger_detector.py
python src/analysis/fairness_metrics.py

# 4. Generate all figures
python src/visualization/visualizations.py
# → figures saved to reports/figures/
```

**Dependencies**: Python 3.10+, packages listed in `requirements.txt` (pandas, numpy, matplotlib, seaborn, scipy, openai, python-dotenv). No API keys are stored in source files; all credentials are read from the `.env` file at runtime.