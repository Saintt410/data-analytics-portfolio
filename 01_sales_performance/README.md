# Sales Performance Analysis

**Business problem:** Revenue is growing but margins are flat — which products, customers and regions create or destroy profit?

**Required CSV columns:** `order_date, customer_id, region, category, sku, revenue, discount, profit`

Run: `python 01_sales_performance/analysis.py [--data your.csv]` → results printed and saved to `01_sales_performance/outputs/`.

The script prints *What the data tells me* findings and *What the business should do next* recommendations computed from the data.
