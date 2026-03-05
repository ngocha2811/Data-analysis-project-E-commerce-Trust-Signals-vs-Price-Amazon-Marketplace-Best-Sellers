# Trust Signals vs Price in Amazon Best Sellers
Python | Pandas | Selenium | Tableau | Data Analysis

### Data Analysis Project | Marketplace Strategy Case Study

This project investigates whether social proof signals (ratings and review volume) show stronger association with sales performance than price variation among Amazon best sellers.

I collected data on 6,000+ Amazon Best Sellers through web scraping, and the analysis explores how social proof dynamics and pricing strategies relate to sales intensity within competitive marketplace environments.

## Project Preview

### Trust Signals vs Sales Performance

<p align="center">
  <img src="visuals/trust_vs_sales_scatter.png" width="800">
</p>



### Review Volume Distribution by Rank Group

<p align="center">
  <img src="visuals/reviews_distribution_rankgroup.png" width="800">
</p>

## Key Insight

- Review volume shows stronger association with sales intensity than price variation.
- Product ratings exhibit limited variation among best sellers, suggesting a minimum quality threshold.
- Price differences alone do not strongly explain differences in sales performance within the top-performing tier.
- Social proof dynamics may reinforce sales momentum through visibility and credibility effects.

These findings highlight the importance of trust accumulation strategies for marketplace sellers competing at the top tier.

## Research Questions

This project investigates three key questions:

### 1. Trust Signals & Sales Performance
Do ratings and review volume meaningfully differentiate product performance among best sellers?

### 2. Price Sensitivity Across Categories
Does the relationship between price and sales vary across product categories?

### 3. What Distinguishes Top-Performing Best Sellers?
Are there measurable structural factors (price level, rating, review volume) that distinguish higher-performing products within the Top 100 rankings?


## Interactive Dashboard

An interactive Tableau dashboard was built to explore:

- Trust signals vs sales intensity
- Category-level price patterns
- Structural characteristics of best sellers

![Tableau Dashboard](visuals/tableau_dashboard.png)

## Project Structure

```
amazon-trust-signals-analysis
│
├── data/
│   ├── raw_data.csv
│   └── cleaned_data.csv
│
├── notebooks/
│   └── exploratory_analysis.ipynb
│
├── visuals/
│   ├── trust_vs_sales_scatter.png
│   ├── reviews_distribution_rankgroup.png
│   └── tableau_dashboard.png
│
├── src/
│   ├── get_product_data.py
│   └── get_bought_number.py
│
├── tableau_dashboard/
│   └── amazon_best_sellers_dashboard.twb
│
└── README.md
```

## Data

The dataset contains 6,000 Amazon Best Seller products, collected via web scraping.

Each record includes:

- Product title
- Price
- Rating
- Review count
- Best seller rank
- Estimated units sold (proxy metric)
- Product URL
- Marketplace
- Collection date

## Skills Demonstrated

- Web scraping with Selenium
- Data cleaning and transformation with Pandas
- Exploratory data analysis with Python
- Correlation analysis
- Data visualization (Matplotlib, Seaborn)
- Interactive dashboard development (Tableau)
- Marketplace strategy interpretation


## Limitations & Future Development

This analysis is correlational and does not establish causal relationships.

Several limitations should be considered:

- Review volume may reflect past sales rather than directly drive future sales.
- Sales performance is approximated using proxy metrics rather than actual transaction data.
- The dataset represents a cross-sectional snapshot and does not capture temporal dynamics.
- Amazon's ranking algorithm includes additional factors (e.g., conversion rate, advertising, fulfillment speed) that are not observable in this dataset.

Future development could extend this analysis by:

- Collecting longitudinal data to study how reviews, price changes, and rankings evolve over time.
- Incorporating additional marketplace signals such as seller reputation, fulfillment method (FBA vs FBM), and advertising activity.
- Applying regression or causal inference methods to better estimate the relative influence of trust signals and price on sales performance.
- Expanding the dataset to include multiple marketplaces or time periods to validate whether the observed patterns remain consistent.


## Author

Data analysis project developed as part of a data analytics bootcamp, focusing on marketplace analytics, e-commerce strategy, and data visualization.