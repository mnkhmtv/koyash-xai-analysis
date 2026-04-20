# Koyash-XAI Analysis - Baseline Pipeline

**Team:** Diana Minnakhmetova · Janna Ivanova · Kseniia Korchagina — Innopolis University, 2026

## 📖 Overview 

This project implements **Contrastive Explanations** (inspired by the Polyjuice framework) to explain and audit predictions of an LLM-based skincare recommendation system.

We investigate **explainability and fairness** in a high-stakes consumer domain where incorrect recommendations can cause skin damage or financial harm. The core idea is counterfactual: the same user query is sent to the LLM twice with a single variable changed (age, skin type, budget, etc.), and we measure how recommendations shift.


**What we analyse:**
- 🪷 **Causal trigger detection** — which input changes drive recommendation changes
- 💲 **Price bias** — do older users get more expensive recommendations?
- 🧖🏼‍♀️ **Tone consistency** — does the model address different demographics differently?
- 📈 **Fairness metrics** — product change rate, avg price diff, tone consistency across 6 change types


## 📂 Project Structure

```bash
koyash-xai-analysis/
├── data/
│   ├── raw/                     # original prompt templates
│   │   └── base_prompts.csv
│   ├── generated/               # generated counterfactual pairs
│   │   └── counterfactual_prompts_no_duplicates.csv
│   ├── responses/               # LLM responses
│   │   └── llm_responses.json
│   ├── processed/               # cleaned and parsed data
│   │   ├── analysis_dataset.csv
│   │   └── triggers.json
│   └── results/                 # fairness metrics
│       └── fairness_report.json
│
├── src/
│   ├── llm/
│   │   ├── api_client.py        # LLM API calls, sending instructions and prompts
│   │   └── batch_api_caller.py  # automatic run of all pairs through LLM
│   │
│   ├── analysis/
│   │   ├── parse_responses.py    # extract products, prices, tone
│   │   ├── recommendation_parser.py # helper functions to extract products
│   │   ├── price_extractor.py        # helper functions to extract prices
│   │   ├── sentiment_analyzer.py      # tone-of-voice analysis
│   │   ├── trigger_detector.py   # detect changes in recommendations
│   │   └── bias_metrics.py       # basic fairness metrics (product/price)
│   │
│   ├── generation/
│   │   ├── prompt_generator.py      # generate counterfactual pairs (future)
│   │   └── demographic_variator.py  # vary age/skin type (future)
│   │
│   └── visualization/
│       ├── visualizations.py    # all 5 figures (main entry point)
│       ├── heatmaps.py          # Figure 2: trigger word heatmap
│       ├── bias_plots.py        # Figure 3: age bias bar chart
│       └── tone_plots.py        # Figure 4: tone consistency line plot
│
├── notebooks/
│   └── demo.ipynb               # pipeline demo
│
├── reports/
│   ├── figures/                 # generated figure PNGs
│   ├── methodology.md           # paper section 3: Methodology & Implementation
│   └── code_appendix.md        # paper Appendix A: pseudocode
│
├── .env.example                  # example file with API keys
├── requirements.txt              # project dependencies
└── README.md                     
```

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

Create a .env file based on .env.example and add your LLM API keys.

## Pipeline

Run all pairs through the LLM API

```bash
python src/llm/batch_api_caller.py
```

Parse responses (products, prices, tone)

```bash
python src/analysis/parse_responses.py
```

Trigger detection (detect changes in products/prices)

```bash
python src/analysis/trigger_detector.py
```

Compute fairness metrics

```bash
python src/analysis/bias_metrics.py
```

Generate all visualisations

```bash
python src/visualization/visualizations.py
```

Figures are saved to `reports/figures/`:

| Figure | Description |
| ------ | ----------- |
| Figure 1 | Dataset statistics |
| Figure 2 | Trigger word heatmap |
| Figure 3 | Age bias bar chart |
| Figure 4 | Tone consistency line plot |
| Figure 5 | Price correlation scatter plot |

Run the interactive demo notebook

```bash
jupyter notebook notebooks/demo.ipynb
```

## Output Files

| File                                                      | Description                         |
| --------------------------------------------------------- | ----------------------------------- |
| `data/generated/counterfactual_prompts_no_duplicates.csv` | Counterfactual prompt pairs         |
| `data/responses/llm_responses.json`                       | All LLM responses                   |
| `data/processed/analysis_dataset.csv`                     | Parsed products, prices, tone       |
| `data/processed/triggers.json`                            | Product/price changes for each pair |
| `data/results/fairness_report.json`                       | Basic bias metrics (age, price)     |
| `reports/figures/`                                        | All 5 generated figure PNGs         |
| `reports/methodology.md`                                  | Paper section 3                     |
| `reports/code_appendix.md`                                | Paper Appendix A: pseudocode        |
