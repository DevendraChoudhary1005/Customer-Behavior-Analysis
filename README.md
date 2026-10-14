# Customer Shopping Behavior Analysis

End-to-end data analysis project: clean a retail customer dataset in **Python**, answer business questions with **PostgreSQL**, and present the results in a **Power BI** dashboard.

![Average purchase by segment](charts/05_avg_purchase_flat.png)

## Overview

The dataset has **3,900 customers** (one row per customer) with demographics, what they bought, how they paid and shipped, discounts, ratings and subscription status. The goal was to understand who the customers are, what drives revenue, and whether subscriptions, discounts or loyalty change how much people spend.

**Headline finding:** spending is almost identical across every segment tested. The average purchase is about **$60** whether the customer is male or female, young or senior, subscribed or not, discounted or not. Revenue differences between segments come from **how many customers** each segment has, not from how much each one spends.

## Key numbers

| Metric | Value |
|---|---|
| Customers | 3,900 |
| Total revenue | $233,081 |
| Average purchase | $59.76 (median $60) |
| Average review rating | 3.75 / 5 |
| Subscribers | 1,053 (27.0%) |
| Orders with a discount | 1,677 (43.0%) |

## Key findings

- **Subscribers do not spend more.** Average spend is $59.49 for subscribers vs $59.87 for non-subscribers, and ratings are identical (3.75).
- **Clothing is 44.7% of revenue** ($104,264) but has the lowest category rating (3.72). Shirt, Jeans and Blouse are the three lowest-rated products.
- **Gender revenue follows customer share.** Males are 68% of customers and bring 67.7% of revenue; per-customer spend is nearly equal ($59.54 male, $60.25 female).
- **Discounts don't create bigger orders.** 43% of orders use a discount, yet discounted orders average $59.28 vs $60.13 without.
- **Repeat buyers (more than 5 previous purchases) subscribe a bit more often** (27.6% vs 22.4%), but the comparison group is small (424 customers), so treat it as a hint.
- **Nothing predicts spend.** Age, previous purchases and rating each have a correlation with purchase amount of about zero (-0.01 to 0.03).

| | |
|---|---|
| ![Revenue by category](charts/01_revenue_by_category.png) | ![Subscription status](charts/03_subscription_donut.png) |
| ![Revenue by age group](charts/06_revenue_by_age_group.png) | ![Top 10 states by revenue](charts/13_top10_states_revenue.png) |

More charts are in the [`charts/`](charts) folder.

## Tech stack

- **Python** (pandas, SQLAlchemy, psycopg2) for cleaning and loading
- **PostgreSQL** and **pgAdmin** for analysis
- **Power BI** for the dashboard
- **Google Colab** for the cleaning notebook

## Project structure

```
customer-shopping-behavior-analysis/
├── data/
│   ├── customer_shopping_behavior.csv   # raw data
│   └── customer.csv                     # cleaned data
├── notebooks/
│   └── data_analysis_on_customer_data.ipynb
├── scripts/
│   └── load_data.py                     # loads customer.csv into PostgreSQL
├── sql/
│   └── analysis_queries.sql             # the 10 business questions
├── charts/                              # PNG charts used in the report
├── dashboard/
│   └── dashboard.png                    # Power BI screenshot
├── report/
│   └── Customer_Shopping_Behavior_Analysis_Report.pdf
└── README.md
```

## Data cleaning

Done in [`notebooks/data_analysis_on_customer_data.ipynb`](notebooks):

1. **Missing values:** only `Review Rating` had nulls (37 rows, 0.9%). They were filled with the median rating of the same category.
2. **Column names:** lowercased with underscores, and `purchase_amount_(usd)` renamed to `purchase_amount`.
3. **`age_group` (new):** four equal-sized quartile bands with `pd.qcut` - Young (18-31), Adult (32-44), Middle-aged (45-57), Senior (58-70).
4. **`purchase_frequency_days` (new):** text frequency (Weekly, Monthly, Quarterly, ...) mapped to a number of days.
5. **Dropped `promo_code_used`:** identical to `discount_applied` in all 3,900 rows.

```python
df['Review Rating'] = df.groupby('Category')['Review Rating'].transform(
    lambda x: x.fillna(x.median()))
df.columns = df.columns.str.lower().str.replace(' ', '_')
df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount'})
df['Age_group'] = pd.qcut(df['age'], q=4, labels=['Young', 'Adult', 'Middle-aged', 'Senior'])
df = df.drop('promo_code_used', axis=1)
df.to_csv('customer.csv', index=False)
```

## How to run it

**1. Clone the repo and install the libraries**

```bash
git clone https://github.com/DevendraChoudhary1005/customer-shopping-behavior-analysis.git
cd customer-shopping-behavior-analysis
pip install pandas sqlalchemy psycopg2-binary
```

**2. Create the database.** Install PostgreSQL, open pgAdmin, and create a database named `customer_behaviour`.

**3. Set your password as an environment variable** (never put it in the code):

```bash
# Windows (Command Prompt)
set PG_PASSWORD=your_password

# Windows (PowerShell)
$env:PG_PASSWORD="your_password"

# macOS / Linux
export PG_PASSWORD=your_password
```

**4. Load the data**

```bash
python scripts/load_data.py
```

It should print `3900`, the number of rows loaded into the `customer` table.

**5. Run the analysis.** Open `sql/analysis_queries.sql` in pgAdmin's Query Tool and run the queries.

## SQL analysis

Ten business questions answered in [`sql/analysis_queries.sql`](sql):

1. Total revenue by gender
2. Customers who used a discount but still spent above the average
3. Top 5 products by average review rating
4. Average purchase: Standard vs Express shipping
5. Do subscribers spend more? (average spend and total revenue)
6. Top 5 products by share of purchases made with a discount
7. Customer segments (New, Returning, Loyal) by previous purchases
8. Top 3 most purchased products within each category
9. Are repeat buyers more likely to subscribe?
10. Revenue contribution by age group

Techniques used: aggregation, `GROUP BY` / `HAVING`, `CASE WHEN`, subqueries, CTEs, and window functions (`ROW_NUMBER`, `SUM() OVER`).

```sql
-- Top 3 most purchased products within each category
WITH item_counts AS (
  SELECT category, item_purchased,
         COUNT(customer_id) AS total_orders,
         ROW_NUMBER() OVER (PARTITION BY category
                            ORDER BY COUNT(customer_id) DESC) AS item_rank
  FROM customer
  GROUP BY category, item_purchased
)
SELECT item_rank, category, item_purchased, total_orders
FROM item_counts
WHERE item_rank <= 3;
```

## Power BI dashboard

![Power BI dashboard](dashboard/dashboard.png)

The dashboard has KPI cards (customers, average purchase, average review rating), a subscription donut, revenue by category, revenue by age group, and slicers for subscription status, gender, category and shipping type. It connects to the PostgreSQL database in Import mode.

## Limitations

- The data has no dates, so trends over time, year-over-year growth and customer lifetime value could not be analysed.
- Almost every segment difference is small, and no significance tests were run. Treat the findings as descriptive, not proven.
- Missing ratings were filled with category medians, which slightly smooths the rating data.
- Age groups are quartile bands, so the names (Young, Adult, Middle-aged, Senior) are labels of convenience.
- Customer segments use thresholds that put about 80% of customers in "Loyal". Quartile-based cut-offs would be more informative.

## Possible next steps

- Add significance tests (t-tests, chi-square) to check whether the small differences are real
- Rebuild the loyalty segments with quartile-based thresholds
- Add RFM-style segmentation if purchase dates become available
- Publish the dashboard to Power BI Service

## Report

The full write-up, with charts and code for every question, is in [`report/`](report).

## Author

**Devendra Choudhary**
B.Tech CSE (AI & ML), JECRC University, Jaipur

- GitHub: [DevendraChoudhary1005](https://github.com/DevendraChoudhary1005)
- LinkedIn: [devendra-choudhary-dc101005](https://linkedin.com/in/devendra-choudhary-dc101005)
