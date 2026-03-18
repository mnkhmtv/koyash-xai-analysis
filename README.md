# Koyash-XAI Analysis - Baseline Pipeline

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
│   └── processed/               # cleaned and parsed data
│       └── analysis_dataset.csv
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
│   └── generation/
│       ├── prompt_generator.py      # generate counterfactual pairs (future)
│       └── demographic_variator.py  # vary age/skin type (future)
│
├── notebooks/
│   └── demo.ipynb                # pipeline demo on 3–5 pairs
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

| File                                                      | Description                         |
| --------------------------------------------------------- | ----------------------------------- |
| `data/generated/counterfactual_prompts_no_duplicates.csv` | Counterfactual prompt pairs         |
| `data/responses/llm_responses.json`                       | All LLM responses                   |
| `data/processed/analysis_dataset.csv`                     | Parsed products, prices, tone       |
| `data/results/triggers.json`                              | Product/price changes for each pair |
| `data/results/fairness_report.json`                       | Basic bias metrics (age, price)     |
