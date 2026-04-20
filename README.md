# Koyash-XAI: Bias Analysis in LLM Skincare Recommendations

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-research-orange)

> An explainable AI (XAI) research project investigating demographic and contextual bias in large language model skincare product recommendations using counterfactual prompt pairs.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Key Results](#key-results)
- [Data Description](#data-description)
- [Requirements](#requirements)
- [License](#license)

---

## Overview

Koyash-XAI investigates whether LLMs exhibit systematic bias when recommending skincare products to users with different demographic profiles. The methodology is **counterfactual**: the same prompt is sent twice — once with a baseline persona and once with a single modified variable (e.g. age, skin type, budget). Differences in recommended products, prices, and response tone are then analysed for fairness.

The pipeline covers the full research workflow: prompt generation → LLM querying → response parsing → trigger detection → fairness metrics → visualisation.

---

## Project Structure

```
koyash-xai-analysis/
├── data/
│   ├── raw/                                         # Base prompt templates
│   │   └── base_prompts.csv
│   ├── generated/                                   # Counterfactual prompt pairs
│   │   └── counterfactual_prompts_no_duplicates.csv
│   ├── responses/                                   # Raw LLM responses
│   │   └── llm_responses.json
│   ├── processed/                                   # Parsed dataset
│   │   ├── analysis_dataset.csv
│   │   └── triggers.json
│   └── results/                                     # Fairness metrics
│       └── fairness_report.json
│
├── src/
│   ├── generation/
│   │   ├── prompt_generator.py                      # Generate counterfactual pairs
│   │   └── demographic_variator.py                  # Vary age / skin type / budget / etc.
│   ├── llm/
│   │   ├── api_client.py                            # LLM API wrapper
│   │   └── batch_api_caller.py                      # Batch all pairs through LLM
│   ├── analysis/
│   │   ├── parse_responses.py                       # Extract products, prices, tone
│   │   ├── recommendation_parser.py                 # Product name extraction
│   │   ├── price_extractor.py                       # Price extraction
│   │   ├── sentiment_analyzer.py                    # Tone-of-voice classifier
│   │   ├── trigger_detector.py                      # Detect recommendation changes
│   │   └── fairness_metrics.py                      # Compute bias metrics
│   └── visualization/
│       ├── visualizations.py                        # All 5 figures (main entry point)
│       ├── heatmaps.py                              # Figure 2: trigger heatmap
│       ├── bias_plots.py                            # Figure 3: age bias bar chart
│       └── tone_plots.py                            # Figure 4: tone consistency
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_bias_analysis.ipynb
│   ├── 03_visual_report.ipynb
│   └── 04_demo.ipynb                                # Full pipeline demo
│
├── reports/
│   ├── figures/                                     # Generated visualisation PNGs
│   ├── methodology.md                               # Paper section 3
│   └── code_appendix.md                             # Paper Appendix A
│
├── .env.example                                     # API key template
├── .gitignore
├── config.yaml
├── requirements.txt
└── README.md
```

---

## Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd koyash-xai-analysis

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API credentials
cp .env.example .env
# Open .env and add your API key:
#   OPENAI_API_KEY=sk-...
```

---

## Usage

Run the pipeline steps in order from the **project root**:

### Step 1 — Generate counterfactual prompts
```bash
python src/generation/prompt_generator.py
```
Reads `data/raw/base_prompts.csv`, applies six demographic/contextual variations, and saves deduplicated pairs to `data/generated/counterfactual_prompts_no_duplicates.csv`.

### Step 2 — Query the LLM
```bash
python src/llm/batch_api_caller.py
```
Sends all prompt pairs to the LLM API and saves raw responses to `data/responses/llm_responses.json`.

### Step 3 — Parse responses
```bash
python src/analysis/parse_responses.py
```
Extracts product names, prices, and tone from each response. Saves to `data/processed/analysis_dataset.csv`.

### Step 4 — Detect triggers
```bash
python src/analysis/trigger_detector.py
```
Compares original vs. modified responses per pair. Records which products changed and the price difference. Saves to `data/processed/triggers.json`.

### Step 5 — Compute fairness metrics
```bash
python src/analysis/fairness_metrics.py
```
Aggregates product change rate, average price difference, and tone consistency per change type. Saves to `data/results/fairness_report.json`.

### Step 6 — Generate all visualisations
```bash
python src/visualization/visualizations.py
```
Produces all five paper figures and saves them to `reports/figures/`.

| Figure | Description |
|--------|-------------|
| Figure 1 | Dataset statistics — pair counts and product change rates |
| Figure 2 | Trigger analysis heatmap — all three metrics across change types |
| Figure 3 | Price bias bar chart — avg price diff, age change highlighted |
| Figure 4 | Tone consistency line plot |
| Figure 5 | Original vs modified price correlation scatter plot |

### Interactive demo
```bash
jupyter notebook notebooks/04_demo.ipynb
```

---

## Key Results

Based on analysis of **75 counterfactual pairs** across 6 change types:

| Metric | Value |
|--------|-------|
| Overall product change rate | **98.67%** |
| Average price difference | **+$1.80** |
| Tone consistency (most change types) | **100%** |
| Tone consistency (ingredient_avoid_change) | **75%** |

**Price bias by change type:**

| Change Type | Avg Price Diff |
|-------------|---------------|
| `ingredient_pref_change` | +$7.38 |
| `budget_change` | +$4.84 |
| `concern_change` | +$3.02 |
| `age_change` | +$1.67 |
| `skin_type_change` | −$0.21 |
| `ingredient_avoid_change` | −$2.84 |

Key finding: the LLM almost always recommends **different products** when any single variable changes, suggesting high sensitivity to prompt context. Age-based changes result in a consistent upward price shift, indicating potential age-related pricing bias.

---

## Data Description

### Change types

| Change Type | Variable Modified |
|-------------|------------------|
| `age_change` | User's stated age |
| `skin_type_change` | Skin type (e.g. oily → dry) |
| `concern_change` | Primary skin concern (e.g. acne → wrinkles) |
| `budget_change` | Budget limit |
| `ingredient_pref_change` | Preferred ingredient |
| `ingredient_avoid_change` | Ingredient to avoid |

### analysis_dataset.csv columns

| Column | Description |
|--------|-------------|
| `pair_id` | Unique pair identifier |
| `change_type` | Dimension varied in this pair |
| `original_products` | Products recommended in baseline response |
| `modified_products` | Products recommended in modified response |
| `original_prices` | Prices extracted from baseline response |
| `modified_prices` | Prices extracted from modified response |
| `original_tone` | Tone label of baseline response |
| `modified_tone` | Tone label of modified response |

---

## Requirements

- Python 3.10+
- OpenAI API key (set in `.env`)
- See `requirements.txt` for full package list

Key packages: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `openai`, `python-dotenv`, `transformers`, `spacy`

---

## License

MIT License — see [LICENSE](LICENSE) for details.