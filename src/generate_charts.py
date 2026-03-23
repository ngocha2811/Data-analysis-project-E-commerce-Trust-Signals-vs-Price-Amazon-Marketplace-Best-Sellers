"""
generate_charts.py
Produces all visuals for the Amazon Best Sellers analysis.
Run from project root: python src/generate_charts.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from scipy import stats
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")

# ── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#0F1117",
    "axes.facecolor":    "#0F1117",
    "axes.edgecolor":    "#2A2D35",
    "axes.labelcolor":   "#C8CAD0",
    "axes.titlecolor":   "#FFFFFF",
    "xtick.color":       "#6B7280",
    "ytick.color":       "#6B7280",
    "text.color":        "#C8CAD0",
    "grid.color":        "#1E2028",
    "grid.linewidth":    0.8,
    "font.family":       "monospace",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  False,
    "axes.spines.bottom": False,
})

# Palette
C_TEAL   = "#2DD4BF"
C_AMBER  = "#F59E0B"
C_PINK   = "#F472B6"
C_MUTED  = "#374151"
C_LIGHT  = "#9CA3AF"
RANK_COLORS = {"Top 10": C_TEAL, "11-50": C_AMBER, "51-100": "#6B7280"}

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("data/clean/product_info_log_rank_group.csv")
df["category_enc"] = LabelEncoder().fit_transform(df["category_name"])
df["market_enc"]   = LabelEncoder().fit_transform(df["market_place"])
RANK_ORDER = ["Top 10", "11-50", "51-100"]

def savefig(name):
    plt.savefig(f"visuals/{name}", dpi=160, bbox_inches="tight",
                facecolor="#0F1117", edgecolor="none")
    plt.close()
    print(f"  saved: visuals/{name}")


# ═══════════════════════════════════════════════════════════════════
# CHART 1 — Key metrics: partial R² bar chart
# ═══════════════════════════════════════════════════════════════════
def chart_partial_r2():
    y_vals = df["log_units_sold"].values
    ss_tot = np.sum((y_vals - y_vals.mean()) ** 2)
    feats  = {
        "Review count": "log_reviews",
        "Price":        "log_price",
        "Rating":       "rating",
        "Marketplace":  "market_enc",
        "Category":     "category_enc",
    }
    r2s = {}
    for label, col in feats.items():
        x = np.column_stack([np.ones(len(df)), df[col].values])
        c, *_ = np.linalg.lstsq(x, y_vals, rcond=None)
        r2s[label] = 1 - np.sum((y_vals - x @ c) ** 2) / ss_tot

    labels = list(r2s.keys())
    values = list(r2s.values())
    colors = [C_TEAL if v == max(values) else C_MUTED for v in values]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(labels, values, color=colors, height=0.55, zorder=3)
    ax.set_xlim(0, max(values) * 1.35)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
    ax.grid(axis="x", zorder=0)
    ax.tick_params(axis="y", labelsize=11)

    for bar, val in zip(bars, values):
        ax.text(val + 0.003, bar.get_y() + bar.get_height() / 2,
                f"R²={val:.3f}", va="center", fontsize=10, color=C_LIGHT)

    ax.set_title("What drives sales intensity?\nVariance explained by each factor alone",
                 fontsize=13, color="#FFFFFF", pad=14, loc="left")
    ax.annotate("Partial R² — each predictor modelled independently against log(units sold)",
                xy=(0, -0.14), xycoords="axes fraction", fontsize=8.5, color="#6B7280")
    fig.tight_layout()
    savefig("01_partial_r2.png")


# ═══════════════════════════════════════════════════════════════════
# CHART 2 — Scatter: log_reviews vs log_units_sold, coloured by rank group
# ═══════════════════════════════════════════════════════════════════
def chart_reviews_vs_sales():
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor("#0F1117")

    for group in RANK_ORDER:
        sub = df[df["rank_group"] == group]
        ax.scatter(sub["log_reviews"], sub["log_units_sold"],
                   color=RANK_COLORS[group], alpha=0.45, s=18,
                   label=group, linewidths=0, zorder=3)

    # regression line (all data)
    m, b, *_ = stats.linregress(df["log_reviews"], df["log_units_sold"])
    xr = np.linspace(df["log_reviews"].min(), df["log_reviews"].max(), 100)
    ax.plot(xr, m * xr + b, color=C_TEAL, linewidth=1.8, alpha=0.9,
            linestyle="--", zorder=4, label=f"Trend  (slope={m:.2f})")

    ax.set_xlabel("log(Review count)", fontsize=11)
    ax.set_ylabel("log(Units sold / month)", fontsize=11)
    ax.set_title("More reviews → more sales\nRelationship holds across all rank groups",
                 fontsize=13, color="#FFFFFF", pad=14, loc="left")
    ax.legend(fontsize=10, framealpha=0, labelcolor="white")
    ax.grid(zorder=0)
    fig.tight_layout()
    savefig("02_reviews_vs_sales.png")


# ═══════════════════════════════════════════════════════════════════
# CHART 3 — Segmentation: median reviews & price by rank group (side-by-side)
# ═══════════════════════════════════════════════════════════════════
def chart_segmentation():
    seg = df.groupby("rank_group").agg(
        med_reviews=("reviews_count", "median"),
        med_price=("price", "median"),
        med_units=("units_sold", "median"),
    ).reindex(RANK_ORDER)

    fig, axes = plt.subplots(1, 3, figsize=(13, 5))
    metrics = [
        ("med_reviews", "Median review count", "{:,.0f}"),
        ("med_price",   "Median price (€)",    "€{:.2f}"),
        ("med_units",   "Median units sold/mo", "{:,.0f}"),
    ]

    for ax, (col, title, fmt) in zip(axes, metrics):
        vals   = seg[col].values
        colors = [RANK_COLORS[g] for g in RANK_ORDER]
        bars   = ax.bar(RANK_ORDER, vals, color=colors, width=0.55, zorder=3)
        ax.set_title(title, fontsize=11, color="#FFFFFF", pad=10)
        ax.tick_params(axis="x", labelsize=10)
        ax.yaxis.set_visible(False)
        ax.grid(axis="y", zorder=0)
        ax.set_ylim(0, max(vals) * 1.25)

        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(vals) * 0.03,
                    fmt.format(val), ha="center", fontsize=10.5, color="#FFFFFF", fontweight="bold")

    # Annotate price chart — key insight
    axes[1].text(0.5, 0.85, "No significant\ndifference",
                 transform=axes[1].transAxes, ha="center", fontsize=9,
                 color=C_AMBER, style="italic")

    fig.suptitle("What separates Top 10 from the rest?\nReviews & sales differ sharply — price does not",
                 fontsize=13, color="#FFFFFF", y=1.02)
    fig.tight_layout()
    savefig("03_segmentation_bars.png")


# ═══════════════════════════════════════════════════════════════════
# CHART 4 — Review distribution boxplot by rank group
# ═══════════════════════════════════════════════════════════════════
def chart_review_distribution():
    fig, ax = plt.subplots(figsize=(8, 5))

    data   = [df[df["rank_group"] == g]["log_reviews"].values for g in RANK_ORDER]
    bp = ax.boxplot(data, patch_artist=True, widths=0.45,
                    medianprops=dict(color="#FFFFFF", linewidth=2),
                    whiskerprops=dict(color="#4B5563"),
                    capprops=dict(color="#4B5563"),
                    flierprops=dict(marker="o", markersize=3,
                                   markerfacecolor="#374151", linestyle="none"))

    for patch, group in zip(bp["boxes"], RANK_ORDER):
        patch.set_facecolor(RANK_COLORS[group])
        patch.set_alpha(0.75)

    ax.set_xticklabels(RANK_ORDER, fontsize=11)
    ax.set_ylabel("log(Review count)", fontsize=11)
    ax.set_title("Review count distribution by rank group\nTop 10 products consistently carry more social proof",
                 fontsize=13, color="#FFFFFF", pad=14, loc="left")
    ax.grid(axis="y", zorder=0)
    fig.tight_layout()
    savefig("04_review_distribution.png")


# ═══════════════════════════════════════════════════════════════════
# CHART 5 — Per-category review elasticity horizontal bar
# ═══════════════════════════════════════════════════════════════════
def chart_category_elasticity():
    cat_rows = []
    for cat in sorted(df["category_name"].unique()):
        sub = df[df["category_name"] == cat]
        if len(sub) < 20:
            continue
        X = np.column_stack([np.ones(len(sub)),
                             sub["log_reviews"].values,
                             sub["log_price"].values,
                             sub["rating"].values])
        c, *_ = np.linalg.lstsq(X, sub["log_units_sold"].values, rcond=None)
        cat_rows.append({"category": cat, "elasticity": round(c[1], 3)})

    cat_df = pd.DataFrame(cat_rows).sort_values("elasticity")
    colors = [C_TEAL if v >= 0.2 else C_MUTED for v in cat_df["elasticity"]]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.barh(cat_df["category"], cat_df["elasticity"],
                   color=colors, height=0.6, zorder=3)
    ax.set_xlim(0, cat_df["elasticity"].max() * 1.4)
    ax.grid(axis="x", zorder=0)
    ax.tick_params(axis="y", labelsize=10)

    for bar, val in zip(bars, cat_df["elasticity"]):
        ax.text(val + 0.004, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=9.5, color=C_LIGHT)

    ax.set_title("Review elasticity by category\n% change in sales per 1% more reviews (holding price & rating constant)",
                 fontsize=12, color="#FFFFFF", pad=14, loc="left")
    ax.set_xlabel("Coefficient (log-log model)", fontsize=10)
    fig.tight_layout()
    savefig("05_category_elasticity.png")


# ═══════════════════════════════════════════════════════════════════
# CHART 6 — Regression coefficient plot (forest plot style)
# ═══════════════════════════════════════════════════════════════════
def chart_regression_coefs():
    # Run full OLS
    features = ["log_reviews", "log_price", "rating", "category_enc", "market_enc"]
    labels   = ["log(Reviews)", "log(Price)", "Rating", "Category", "Marketplace"]
    X = np.column_stack([np.ones(len(df))] + [df[f].values for f in features])
    y = df["log_units_sold"].values
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    ss_res = np.sum((y - X @ c) ** 2)
    n, k = X.shape
    mse  = ss_res / (n - k)
    se   = np.sqrt(np.diag(mse * np.linalg.inv(X.T @ X)))
    coefs = c[1:]
    ses   = se[1:]
    ci95  = 1.96 * ses

    fig, ax = plt.subplots(figsize=(8, 5))
    ys = range(len(labels))
    colors = [C_TEAL if abs(coefs[i]) > ci95[i] else C_MUTED for i in range(len(coefs))]

    ax.barh(ys, coefs, color=colors, height=0.45, zorder=3, alpha=0.85)
    ax.errorbar(coefs, ys, xerr=ci95, fmt="none",
                ecolor="#FFFFFF", elinewidth=1.5, capsize=5, zorder=4)
    ax.axvline(0, color="#6B7280", linewidth=1, linestyle="--", zorder=2)

    ax.set_yticks(list(ys))
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel("Coefficient (log_units_sold scale)", fontsize=10)
    ax.set_title("OLS regression coefficients with 95% CI\nAll predictors except Category are significant",
                 fontsize=12, color="#FFFFFF", pad=14, loc="left")
    ax.grid(axis="x", zorder=0)

    sig_patch   = mpatches.Patch(color=C_TEAL,  label="Significant (p<0.05)")
    insig_patch = mpatches.Patch(color=C_MUTED, label="Not significant")
    ax.legend(handles=[sig_patch, insig_patch], fontsize=9,
              framealpha=0, labelcolor="white", loc="lower right")
    fig.tight_layout()
    savefig("06_regression_coefs.png")


# ═══════════════════════════════════════════════════════════════════
# CHART 7 — Price vs rank group violin (showing it doesn't differ)
# ═══════════════════════════════════════════════════════════════════
def chart_price_by_rank():
    fig, ax = plt.subplots(figsize=(8, 5))
    data   = [df[df["rank_group"] == g]["log_price"].values for g in RANK_ORDER]

    parts = ax.violinplot(data, positions=[0, 1, 2], showmedians=True,
                          showextrema=False)
    for i, (pc, group) in enumerate(zip(parts["bodies"], RANK_ORDER)):
        pc.set_facecolor(RANK_COLORS[group])
        pc.set_alpha(0.6)
    parts["cmedians"].set_color("#FFFFFF")
    parts["cmedians"].set_linewidth(2)

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(RANK_ORDER, fontsize=11)
    ax.set_ylabel("log(Price)", fontsize=11)
    ax.set_title("Price distribution by rank group\nOverlapping distributions — price does not separate rank tiers",
                 fontsize=12, color="#FFFFFF", pad=14, loc="left")

    # Annotation: KW p-value
    ax.text(0.98, 0.92, "Kruskal-Wallis p = 0.083\n(not significant)",
            transform=ax.transAxes, ha="right", fontsize=9,
            color=C_AMBER, style="italic",
            bbox=dict(facecolor="#1A1D24", edgecolor="#374151",
                      boxstyle="round,pad=0.4"))
    ax.grid(axis="y", zorder=0)
    fig.tight_layout()
    savefig("07_price_distribution.png")


if __name__ == "__main__":
    print("Generating charts...")
    chart_partial_r2()
    chart_reviews_vs_sales()
    chart_segmentation()
    chart_review_distribution()
    chart_category_elasticity()
    chart_regression_coefs()
    chart_price_by_rank()
    print("All charts saved to visuals/")
