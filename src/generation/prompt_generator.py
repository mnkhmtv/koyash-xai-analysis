import pandas as pd
import itertools
import random

# ===== PARAMETERS =====
AGES = [20, 25, 30, 35, 40, 45, 50]
SKIN_TYPES = ["oily", "dry", "combination", "normal"]
CONCERNS = ["acne", "wrinkles", "dryness", "pigmentation", "redness"]
SENSITIVITIES = ["sensitive", ""]
BUDGETS = ["low", "medium", "high"]
INGREDIENT_PREF = ["natural ingredients", "retinol", "vitamin C", "hyaluronic acid", "niacinamide"]
INGREDIENT_AVOID = ["alcohol", "fragrance", "retinol", "acids", "parabens"]

# ===== TEMPLATES =====
TEMPLATES = {
    "T01": "I am {age}, I have {skin_type} skin, and my concern is {concern}. What would you recommend?",
    "T02": "Hi! I'm {age}, my skin type is {skin_type}, and I'm dealing with {concern}. Any recommendations?",
    "T03": "I am {age}, I have {skin_type} and {sensitivity} skin, with {concern} as my main issue. What should I use?",
    "T04": "I am {age}, I have {skin_type} skin and {concern}. My budget is {budget}. What products would you suggest?",
    "T05": "I am {age}, I have {skin_type} skin with {concern}. Can you suggest a skincare routine?",
    "T06": "I am {age}, I have {skin_type} skin with {concern} and also {concern_2}. What would work best?",
    "T07": "I am {age}, I have {skin_type} skin and struggle with {concern}. What would be a safe and gentle option?",
    "T08": "I'm {age} and honestly tired of dealing with {concern}. My skin is {skin_type}. Please help me find something that works.",
    "T09": "I am {age} with {skin_type} skin and {concern}. I would prefer products with {ingredient_pref}. Any suggestions?",
    "T10": "I am {age}, I have {skin_type} skin and {concern}, but I want to avoid {ingredient_avoid}. What should I choose?"
}

# ===== PAIR GENERATOR =====
def fill_template(template, params):
    return template.format(**params)

def generate_pairs():
    pairs = []
    pair_id = 1

    # Base parameters for each pair
    base_params = {
        "age": 25,
        "skin_type": "oily",
        "concern": "acne",
        "sensitivity": "sensitive",
        "budget": "medium",
        "concern_2": "dryness",
        "ingredient_pref": "niacinamide",
        "ingredient_avoid": "alcohol"
    }

    # T01-T07: Core templates (70%) — age, skin_type, concern, sensitivity, budget
    core_templates = ["T01", "T02", "T04", "T05", "T07"]

    for template_id in core_templates:
        template = TEMPLATES[template_id]

        # age_change
        for age in AGES:
            modified_params = base_params.copy()
            modified_params["age"] = age
            pairs.append({
                "pair_id": pair_id,
                "template_id": template_id,
                "change_type": "age_change",
                "original_query": fill_template(template, base_params),
                "modified_query": fill_template(template, modified_params),
                "original_value": base_params["age"],
                "modified_value": age
            })
            pair_id += 1

        # skin_type_change
        for skin in SKIN_TYPES:
            modified_params = base_params.copy()
            modified_params["skin_type"] = skin
            pairs.append({
                "pair_id": pair_id,
                "template_id": template_id,
                "change_type": "skin_type_change",
                "original_query": fill_template(template, base_params),
                "modified_query": fill_template(template, modified_params),
                "original_value": base_params["skin_type"],
                "modified_value": skin
            })
            pair_id += 1

        # concern_change
        for concern in CONCERNS:
            modified_params = base_params.copy()
            modified_params["concern"] = concern
            pairs.append({
                "pair_id": pair_id,
                "template_id": template_id,
                "change_type": "concern_change",
                "original_query": fill_template(template, base_params),
                "modified_query": fill_template(template, modified_params),
                "original_value": base_params["concern"],
                "modified_value": concern
            })
            pair_id += 1

    # T03: sensitivity_change
    for sensitivity in SENSITIVITIES:
        modified_params = base_params.copy()
        modified_params["sensitivity"] = sensitivity
        pairs.append({
            "pair_id": pair_id,
            "template_id": "T03",
            "change_type": "sensitivity_change",
            "original_query": fill_template(TEMPLATES["T03"], base_params),
            "modified_query": fill_template(TEMPLATES["T03"], modified_params),
            "original_value": base_params["sensitivity"],
            "modified_value": sensitivity
        })
        pair_id += 1

    # T04: budget_change
    for budget in BUDGETS:
        modified_params = base_params.copy()
        modified_params["budget"] = budget
        pairs.append({
            "pair_id": pair_id,
            "template_id": "T04",
            "change_type": "budget_change",
            "original_query": fill_template(TEMPLATES["T04"], base_params),
            "modified_query": fill_template(TEMPLATES["T04"], modified_params),
            "original_value": base_params["budget"],
            "modified_value": budget
        })
        pair_id += 1

    # T09: ingredient_pref_change
    for pref in INGREDIENT_PREF:
        modified_params = base_params.copy()
        modified_params["ingredient_pref"] = pref
        pairs.append({
            "pair_id": pair_id,
            "template_id": "T09",
            "change_type": "ingredient_pref_change",
            "original_query": fill_template(TEMPLATES["T09"], base_params),
            "modified_query": fill_template(TEMPLATES["T09"], modified_params),
            "original_value": base_params["ingredient_pref"],
            "modified_value": pref
        })
        pair_id += 1

    # T10: ingredient_avoid_change
    for avoid in INGREDIENT_AVOID:
        modified_params = base_params.copy()
        modified_params["ingredient_avoid"] = avoid
        pairs.append({
            "pair_id": pair_id,
            "template_id": "T10",
            "change_type": "ingredient_avoid_change",
            "original_query": fill_template(TEMPLATES["T10"], base_params),
            "modified_query": fill_template(TEMPLATES["T10"], modified_params),
            "original_value": base_params["ingredient_avoid"],
            "modified_value": avoid
        })
        pair_id += 1

    return pd.DataFrame(pairs)

if __name__ == "__main__":
    df = generate_pairs()
    df.to_csv("data/generated/counterfactual_prompts.csv", index=False)
    print(f"Generated {len(df)} pairs")
    print(df.head())