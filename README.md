# Why Price Doesn’t Matter on Amazon Best Sellers?
### A Data Analysis of Trust-Driven Sales

`Python` `Pandas` `NumPy` `SciPy` `Matplotlib` `Selenium` `Tableau`

---

Author: Ngoc Ha Nguyen - [LinkedIn](https://www.linkedin.com/in/hannah-ngocha-nguyen)

---

## The Question

Amazon best sellers compete on two levers sellers can actually control: **price** and **social proof** (ratings + review volume). Which one matters more?

This project collects 4,000 Amazon Best Seller products across 15 categories and 5 European marketplaces, then uses regression and segmentation analysis to quantify the relationship between trust signals, price, and sales intensity.

---

## Key Findings

**1. Review volume is the strongest predictor of sales intensity**
A 10% increase in review count is associated with ~2.7% more units sold, holding price and rating constant (OLS, p < 0.001).

**2. Price does not separate top performers from the rest**
Top 10 products have a median price of €15.19. Products ranked 51–100 have a median of €14.99. The difference is not statistically significant (Mann-Whitney U, p = 0.60).

**3. Top 10 products carry 3× more reviews than rank 51–100 products**
Median review count: 9,428 (Top 10) vs 3,163 (51–100). This difference is highly significant (p < 0.001).

**4. The pattern is consistent across categories**
Category is not a significant predictor in the global model (p = 0.62), suggesting social proof dynamics operate similarly regardless of product type.

**5. Review elasticity varies by category**
Amazon Devices (0.41) and Lighting (0.25) are most review-driven. Fashion (0.06) and Auto (0.06) are least — where brand or compatibility likely dominate purchase decisions.

[→ Full analysis notebook](notebooks/02_analysis.ipynb)

---

## Visuals

### What drives sales intensity?
![Partial R²](visuals/01_partial_r2.png)
*Review count explains 14% of variance in sales intensity on its own — more than price, rating, marketplace, or category combined.*

### Reviews vs Sales
![Reviews vs Sales](visuals/02_reviews_vs_sales.png)
*Positive relationship holds consistently across all rank tiers.*

[→ View on Tableau Public](https://public.tableau.com/app/profile/ngoc.ha.nguyen1781/viz/amazon_best_sellers_dashboard/Dashboard1)

### What separates Top 10 from the rest?
![Segmentation](visuals/03_segmentation_bars.png)
*Reviews and units sold differ sharply across rank groups. Price does not.*

### Price distribution by rank group
![Price distribution](visuals/07_price_distribution.png)
*Overlapping price distributions confirm that price is not the differentiating factor between rank tiers.*

### Regression coefficients with 95% CI
![Regression](visuals/06_regression_coefs.png)
*OLS model: all predictors significant except category — the review-sales relationship holds broadly.*

### Review elasticity by category
![Category elasticity](visuals/05_category_elasticity.png)
*Per-category regressions reveal where social proof matters most.*

---

## Methodology

### Data collection
- Scraped Amazon Best Seller pages using **Selenium** across 5 marketplaces (DE, ES, UK, FR, IT)
- Collected product title, price, rating, review count, rank, and 'bought last month' badge
- ~4,000 products across 15 categories (100 per category per marketplace)

### Variable construction
- `log_units_sold` — outcome variable; log of the 'bought last month' figure (proxy for sales intensity)
- `log_reviews`, `log_price` — log-transformed to compress skew and enable elasticity interpretation
- `rank_group` — segmented into Top 10 / 11–50 / 51–100

### Analysis
| Step | Method | Purpose |
|------|--------|---------|
| Global regression | OLS (numpy lstsq) | Quantify relative effect sizes with inference |
| Partial R² | Single-predictor OLS | Rank predictors by independent explanatory power |
| Segmentation | Kruskal-Wallis + Mann-Whitney U | Test whether rank groups differ statistically |
| Category breakdown | Per-category OLS | Check whether review elasticity varies by product type |

### Limitations
- Correlational — cannot establish causal direction between reviews and sales
- Outcome is a proxy metric (rounded bucket, not actual transaction data)
- Single cross-sectional snapshot — no temporal dynamics
- Amazon's algorithm includes unobservable factors (conversion rate, advertising, FBA status)

---

## Interactive Dashboard

Explore trust signals vs sales intensity, category-level patterns, and rank group characteristics in the Tableau dashboard:

[→ View on Tableau Public](https://public.tableau.com/app/profile/ngoc.ha.nguyen1781/viz/amazon_best_sellers_dashboard/Dashboard1)

---

## Project Structure

```
amazon-trust-signals-analysis/
│
├── data/
│   ├── raw/                        # Original scraped data
│   └── clean/
│       └── product_info_log_rank_group.csv
│
├── notebooks/
│   └── analysis.ipynb              # Full analysis with narrative
│
├── src/
│   ├── get_product_data.py         # Selenium scraper
│   ├── get_bought_number.py        # Units sold extraction
│   └── generate_charts.py         # All chart generation
│
├── visuals/                        # Output charts
│
└── README.md
```

---

## Reproducing the Analysis

```bash
# 1. Install dependencies
pip install pandas numpy scipy scikit-learn matplotlib seaborn selenium

# 2. Generate all charts
python src/generate_charts.py

# 3. Open the notebook
jupyter notebook notebooks/analysis.ipynb
```

No non-standard dependencies. The regression uses `numpy.linalg.lstsq` directly — no statsmodels required.

---

## Author

**Ngoc Ha Nguyen**  
[LinkedIn](https://www.linkedin.com/in/hannah-ngocha-nguyen)
