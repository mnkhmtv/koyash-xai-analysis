# Explaining a Skincare Recommender with Contrastive XAI

Large language models are increasingly used as product advisors, but their behavior is often opaque. In our project, we audited an LLM-based skincare recommender with a simple question in mind: if we change just one user attribute, does the model react in a predictable way?

This is where Explainable AI, or XAI, becomes useful. Instead of asking only whether the model is accurate, XAI asks why it behaves the way it does. For a skincare assistant, that matters because recommendation changes can affect not only relevance, but also price, tone, and safety.

In this post, we walk through the contrastive XAI pipeline we built for the **Koyash-XAI** project:

- how we generated counterfactual prompt pairs,
- how we queried the model,
- how we parsed the responses,
- how we measured product, price, and tone changes,
- and what the results tell us about the model's behavior.

The goal is not to prove that the model is "good" or "bad". The goal is to make its behavior visible.

---

## What is contrastive XAI?

If you already know ML, the easiest way to think about contrastive XAI is this:

> Instead of explaining a single prediction from model internals, we compare two nearly identical inputs and observe what changes.

That idea is especially useful when the model is a black box or when the output is free-form text rather than a class label.

In our setting, the input is a skincare prompt like:

> "I am 25, I have oily skin, and my concern is acne. What would you recommend?"

Then we create a second prompt where exactly one attribute changes:

> "I am 45, I have oily skin, and my concern is acne. What would you recommend?"

If the recommended products, prices, or tone change, we can use that difference as an explanation signal.

This is contrastive XAI in practice:

1. create a minimal edit,
2. query the model on both versions,
3. compare the outputs,
4. measure how sensitive the model is to the changed attribute.

---

## Step 1: Build counterfactual prompt pairs

We started with a set of base skincare templates and turned them into counterfactual pairs. Each pair differed in only one factor:

- age
- skin type
- concern
- budget
- preferred ingredient
- avoided ingredient

That gave us **75 prompt pairs** in total.

The generation logic is straightforward:

```python
AGES = [20, 25, 30, 35, 40, 45, 50]
SKIN_TYPES = ["oily", "dry", "combination", "normal"]
CONCERNS = ["acne", "wrinkles", "dryness", "pigmentation", "redness"]
BUDGETS = ["low", "medium", "high"]
INGREDIENT_PREF = ["natural ingredients", "retinol", "vitamin C", "hyaluronic acid", "niacinamide"]
INGREDIENT_AVOID = ["alcohol", "fragrance", "retinol", "acids", "parabens"]
```

The important part is that we do not change everything at once. We change one attribute, keep the rest fixed, and ask whether the output changes. That is what makes the comparison interpretable.

---

## Step 2: Query the LLM

Next, we sent both prompts in each pair to the model separately.

The system prompt framed the LLM as a skincare advisor, and the user prompt contained the query itself. This part is important because the analysis depends on the outputs being independent:

```python
original_response = api_client.complete(
    system="You are a professional skincare advisor.",
    user=pair.original_prompt
)

modified_response = api_client.complete(
    system="You are a professional skincare advisor.",
    user=pair.modified_prompt
)
```

At this stage, the model produces plain text. The text may include product names, prices, explanations, and tone markers such as "recommend", "avoid", or "suitable".

That means the next step is parsing.

---

## Step 3: Parse the responses

We extracted three types of signals from each response:

1. product names
2. prices
3. tone

### Product extraction

For product names, we used a regex-plus-heuristics approach because the output is not structured. Skincare responses often contain brand names and item names in a semi-consistent format, but the exact formatting can vary.

### Price extraction

Prices were extracted with regular expressions and then averaged per response.

### Tone detection

Tone was detected with a lightweight rule-based classifier:

```python
def detect_tone(text: str) -> str:
    if not text:
        return "neutral"

    text = text.lower()

    positive_words = ["recommend", "great", "effective", "good", "best", "suitable"]
    negative_words = ["avoid", "not recommended", "bad", "irritating", "harmful"]

    pos_score = sum(word in text for word in positive_words)
    neg_score = sum(word in text for word in negative_words)

    if pos_score > neg_score:
        return "positive"
    elif neg_score > pos_score:
        return "negative"
    else:
        return "neutral"
```

This is not a deep sentiment model. It is intentionally simple because our goal is not to build a perfect tone classifier. Our goal is to test whether tone changes at all when the prompt changes.

---

## Step 4: Detect triggers

After parsing, we compared the two outputs in each pair.

The core trigger logic was:

```python
original_products = set(ast.literal_eval(row["original_products"]))
modified_products = set(ast.literal_eval(row["modified_products"]))

product_changed = original_products != modified_products

avg_orig = sum(orig_prices) / len(orig_prices) if orig_prices else 0
avg_mod = sum(mod_prices) / len(mod_prices) if mod_prices else 0
price_diff = round(avg_mod - avg_orig, 2)
```

This gave us a simple but useful set of metrics:

- product change rate
- average price difference
- tone consistency

The point is not just to count changes, but to understand *which attributes* cause the changes.

---

## What the figures show

The figures below summarize the behavior of the model across the six perturbation types.

### Figure 1. Dataset overview

![Figure 1: Dataset Overview](reports/figures/figure1_dataset_statistics.png)

Figure 1 shows two things at once: how many pairs we had per change type, and how often the recommended products changed. The key observation is that product change is near-universal — **98.67% of pairs** produced different recommendations when a single attribute changed.

### Figure 2. Trigger analysis heatmap

![Figure 2: Trigger Analysis Heatmap](reports/figures/figure2_trigger_heatmap.png)

Figure 2 combines the three main metrics in one view: product change rate, average price difference, and tone change rate. The strongest upward price shift appears for ingredient preference changes (+$7.38 on average), while ingredient avoidance is the only category where tone changes meaningfully.

### Figure 3. Price bias by change type

![Figure 3: Price Bias by Change Type](reports/figures/figure3_age_bias.png)

Figure 3 shows the average price difference per change type with error bars. The largest price increases come from ingredient preference (+$7.38) and budget changes (+$4.84). Age produces a smaller but consistent upward shift (+$1.67). Skin type is close to neutral (−$0.21), and ingredient avoidance is the only type that consistently leads to cheaper recommendations (−$2.84) — which makes intuitive sense, as avoiding harsh actives often shifts the model toward more basic, affordable products.

### Figure 4. Tone consistency

![Figure 4: Tone Consistency by Change Type](reports/figures/figure4_tone_consistency.png)

Figure 4 is the simplest one: tone is 100% consistent across five of six change types. The exception is ingredient avoidance, where 25% of pairs show a tone shift. That suggests the model treats avoidance prompts as a qualitatively different kind of request.

### Figure 5. Price correlation scatter plot

![Figure 5: Original vs Modified Price Correlation](reports/figures/figure5_price_correlation.png)

Figure 5 compares original and modified mean prices pair by pair. Points above the diagonal indicate cases where the modified prompt led to more expensive recommendations. The spread around the diagonal shows that the model does not follow a single consistent pricing rule — the same type of edit can push prices up or down depending on context.

---

## What we learned

The main takeaway is that the model is sensitive, but not uniformly stable.

From an XAI perspective, that is useful because it means contrastive analysis reveals real differences in output behavior. From a product perspective, it is also concerning because the same prompt structure can produce different product choices, different prices, and sometimes different tone depending on a single input attribute.

Three patterns stand out:

1. **Product recommendations almost always change** when a single input attribute changes (98.67% of pairs).
2. **Price often increases**, most strongly for ingredient preference (+$7.38) and budget (+$4.84) changes. Age produces a consistent upward shift (+$1.67).
3. **Tone is stable in most cases**, but ingredient avoidance is a systematic exception — it reliably shifts the model toward cheaper products and sometimes changes its tone.

So what does that mean?

It means the model is not just recommending products. It is also expressing implicit preferences about price level and response style that depend on the user profile. In a consumer-health setting, that is exactly the kind of behavior we want to inspect before deployment.

---

## Reproduce the analysis

The full pipeline is organized in the repository. Run the steps in order from the project root:

```bash
python src/generation/prompt_generator.py
python src/llm/batch_api_caller.py
python src/analysis/parse_responses.py
python src/analysis/trigger_detector.py
python src/analysis/fairness_metrics.py
python src/visualization/visualizations.py
```

The outputs are saved to:

- `data/generated/counterfactual_prompts_no_duplicates.csv`
- `data/responses/llm_responses.json`
- `data/processed/analysis_dataset.csv`
- `data/processed/triggers.json`
- `data/results/fairness_report.json`
- `reports/figures/`

To explore the results interactively, open the demo notebook:

```bash
jupyter notebook notebooks/demo.ipynb
```

The notebook covers data loading, metric summary, and all five figures in a single runnable document.

---

## Final note

XAI is most useful when it makes model behavior visible in a form that humans can inspect. In this project, the contrastive setup made that possible with a small number of carefully designed prompt edits.

The model may still look fluent, but now we can ask a more precise question:

> What exactly changed, and why?

That is the kind of question XAI is meant to answer.