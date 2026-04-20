import ast
import json
import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DATASET_PATH = "data/processed/analysis_dataset.csv"
TRIGGERS_PATH = "data/processed/triggers.json"
FAIRNESS_PATH = "data/results/fairness_report.json"
FIGURES_DIR = "reports/figures"

PALETTE = sns.color_palette("Set2", 6)
CHANGE_TYPES = [
    "age_change",
    "skin_type_change",
    "concern_change",
    "budget_change",
    "ingredient_pref_change",
    "ingredient_avoid_change",
]
TYPE_COLOR = {ct: PALETTE[i] for i, ct in enumerate(CHANGE_TYPES)}
LABELS = {
    "age_change": "Age",
    "skin_type_change": "Skin Type",
    "concern_change": "Concern",
    "budget_change": "Budget",
    "ingredient_pref_change": "Ingr. Pref.",
    "ingredient_avoid_change": "Ingr. Avoid",
}

sns.set_theme(style="whitegrid", font_scale=1.1)


def _mean_price(price_str):
    try:
        prices = [float(p) for p in ast.literal_eval(price_str) if p]
        return sum(prices) / len(prices) if prices else np.nan
    except Exception:
        return np.nan


def _save(fig, save_path):
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  saved -> {save_path}")


def plot_dataset_statistics(df, triggers_df, save_path=None):
    counts = df["change_type"].value_counts().reindex(CHANGE_TYPES).fillna(0)
    change_rate = (
        triggers_df.groupby("change_type")["product_changed"]
        .mean()
        .reindex(CHANGE_TYPES)
        .fillna(0)
        * 100
    )
    xlabels = [LABELS[ct] for ct in CHANGE_TYPES]
    colors = [TYPE_COLOR[ct] for ct in CHANGE_TYPES]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Figure 1: Dataset Overview", fontsize=14, fontweight="bold")

    bars = axes[0].bar(xlabels, counts.values, color=colors, edgecolor="white")
    axes[0].set_title("Pair Count per Change Type")
    axes[0].set_ylabel("Number of pairs")
    axes[0].set_xlabel("Change type")
    for bar in bars:
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            str(int(bar.get_height())),
            ha="center",
            va="bottom",
            fontsize=10,
        )

    bars2 = axes[1].bar(xlabels, change_rate.values, color=colors, edgecolor="white")
    axes[1].set_title("Product Change Rate per Change Type")
    axes[1].set_ylabel("Product change rate (%)")
    axes[1].set_xlabel("Change type")
    axes[1].set_ylim(0, 115)
    for bar in bars2:
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{bar.get_height():.0f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    _save(fig, save_path)
    plt.show()
    return fig


def plot_trigger_heatmap(df, triggers_df, save_path=None):
    df = df.copy()
    df["tone_changed"] = (
        df["original_tone"].str.strip().str.lower()
        != df["modified_tone"].str.strip().str.lower()
    ).astype(float)

    merged = triggers_df.merge(
        df[["pair_id", "tone_changed"]], on="pair_id", how="left"
    )
    grp = merged.groupby("change_type")

    prod_rate = grp["product_changed"].mean().reindex(CHANGE_TYPES)
    price_diff = grp["price_diff"].mean().reindex(CHANGE_TYPES)
    tone_rate = grp["tone_changed"].mean().reindex(CHANGE_TYPES).fillna(0)

    raw = pd.DataFrame(
        {
            "Product\nChange Rate": prod_rate.values,
            "Avg Price\nDiff ($)": price_diff.values,
            "Tone\nChange Rate": tone_rate.values,
        },
        index=[LABELS[ct] for ct in CHANGE_TYPES],
    )

    norm = raw.copy()
    for col in norm.columns:
        col_min, col_max = norm[col].min(), norm[col].max()
        if col_max != col_min:
            norm[col] = (norm[col] - col_min) / (col_max - col_min)
        else:
            norm[col] = 0.5

    annot = pd.DataFrame(index=raw.index, columns=raw.columns)
    annot["Product\nChange Rate"] = raw["Product\nChange Rate"].map("{:.0%}".format)
    annot["Avg Price\nDiff ($)"] = raw["Avg Price\nDiff ($)"].map("${:.2f}".format)
    annot["Tone\nChange Rate"] = raw["Tone\nChange Rate"].map("{:.0%}".format)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        norm,
        annot=annot,
        fmt="",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        cbar_kws={"label": "Normalised score"},
    )
    ax.set_title(
        "Figure 2: Trigger Analysis Heatmap",
        fontsize=14,
        fontweight="bold",
        pad=12,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Change type")
    plt.tight_layout()
    _save(fig, save_path)
    plt.show()
    return fig


def plot_age_bias(triggers_df, save_path=None):
    grp = triggers_df.groupby("change_type")["price_diff"]
    means = grp.mean().reindex(CHANGE_TYPES)
    stds = grp.std().reindex(CHANGE_TYPES).fillna(0)
    xlabels = [LABELS[ct] for ct in CHANGE_TYPES]
    colors = ["#E84A5F" if ct == "age_change" else "#5B8CBA" for ct in CHANGE_TYPES]

    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.bar(
        xlabels,
        means.values,
        yerr=stds.values,
        capsize=5,
        color=colors,
        edgecolor="white",
        error_kw={"elinewidth": 1.5},
    )
    ax.axhline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.6)

    for bar, mean_val in zip(bars, means.values):
        va = "bottom" if mean_val >= 0 else "top"
        offset = 0.3 if mean_val >= 0 else -0.3
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            mean_val + offset,
            f"${mean_val:.2f}",
            ha="center",
            va=va,
            fontsize=9.5,
        )

    handles = [
        mpatches.Patch(color="#E84A5F", label="Age change (highlighted)"),
        mpatches.Patch(color="#5B8CBA", label="Other change types"),
    ]
    ax.legend(handles=handles, loc="upper right")
    ax.set_title(
        "Figure 3: Price Bias by Change Type",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_ylabel("Average price difference ($)\n(modified − original)")
    ax.set_xlabel("Change type")
    plt.tight_layout()
    _save(fig, save_path)
    plt.show()
    return fig


def plot_tone_consistency(fairness_report, save_path=None):
    tone_data = fairness_report.get("tone_consistency_by_change_type", {})
    types = [ct for ct in CHANGE_TYPES if ct in tone_data]
    values = [tone_data[ct] for ct in types]
    xlabels = [LABELS[ct] for ct in types]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        xlabels,
        values,
        marker="o",
        linewidth=2.5,
        color="#2E86AB",
        markersize=8,
        markerfacecolor="white",
        markeredgewidth=2.5,
    )
    ax.fill_between(xlabels, values, alpha=0.12, color="#2E86AB")

    for x, y in zip(xlabels, values):
        ax.annotate(
            f"{y:.0%}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=9.5,
        )

    ax.set_ylim(0, 1.15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_title(
        "Figure 4: Tone Consistency by Change Type",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_ylabel("Tone consistency")
    ax.set_xlabel("Change type")
    plt.tight_layout()
    _save(fig, save_path)
    plt.show()
    return fig


def plot_price_correlation(df, triggers_df, save_path=None):
    df = df.copy()
    df["orig_mean"] = df["original_prices"].apply(_mean_price)
    df["mod_mean"] = df["modified_prices"].apply(_mean_price)
    df = df.dropna(subset=["orig_mean", "mod_mean"])

    fig, ax = plt.subplots(figsize=(10, 8))

    for ct in CHANGE_TYPES:
        sub = df[df["change_type"] == ct]
        if sub.empty:
            continue
        ax.scatter(
            sub["orig_mean"],
            sub["mod_mean"],
            color=TYPE_COLOR[ct],
            label=LABELS[ct],
            s=70,
            alpha=0.8,
            edgecolors="white",
            linewidths=0.5,
        )

    lo = min(df["orig_mean"].min(), df["mod_mean"].min()) - 2
    hi = max(df["orig_mean"].max(), df["mod_mean"].max()) + 2
    ax.plot(
        [lo, hi],
        [lo, hi],
        "--",
        color="grey",
        linewidth=1.2,
        alpha=0.7,
        label="y = x  (no change)",
    )
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)

    ax.set_title(
        "Figure 5: Original vs Modified Price Correlation",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Mean original price ($)")
    ax.set_ylabel("Mean modified price ($)")
    ax.legend(title="Change type", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    _save(fig, save_path)
    plt.show()
    return fig


if __name__ == "__main__":
    print("Loading data...")
    df = pd.read_csv(DATASET_PATH)
    triggers_df = pd.DataFrame(json.load(open(TRIGGERS_PATH, encoding="utf-8")))
    fairness = json.load(open(FAIRNESS_PATH, encoding="utf-8"))

    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("Figure 1...")
    plot_dataset_statistics(
        df,
        triggers_df,
        save_path=f"{FIGURES_DIR}/figure1_dataset_statistics.png",
    )

    print("Figure 2...")
    plot_trigger_heatmap(
        df,
        triggers_df,
        save_path=f"{FIGURES_DIR}/figure2_trigger_heatmap.png",
    )

    print("Figure 3...")
    plot_age_bias(
        triggers_df,
        save_path=f"{FIGURES_DIR}/figure3_age_bias.png",
    )

    print("Figure 4...")
    plot_tone_consistency(
        fairness,
        save_path=f"{FIGURES_DIR}/figure4_tone_consistency.png",
    )

    print("Figure 5...")
    plot_price_correlation(
        df,
        triggers_df,
        save_path=f"{FIGURES_DIR}/figure5_price_correlation.png",
    )

    print(f"\nDone! All figures saved to {FIGURES_DIR}")
