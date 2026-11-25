# Data Analytics Portfolio

Five end-to-end business analytics projects in Python. Each answers:
1. **What is the business problem?**
2. **What does the data tell me?**
3. **What should the business do next?**

| # | Project | Folder |
|---|---------|--------|
| 01 | Sales Performance Analysis | `01_sales_performance/` |
| 02 | Customer Churn Analysis | `02_customer_churn/` |
| 03 | Marketing Campaign Analysis | `03_marketing_campaigns/` |
| 04 | E-commerce Customer Analysis | `04_ecommerce_customers/` |
| 05 | Employee Attrition Analysis | `05_employee_attrition/` |

## Quick start (anyone can reuse this)
```bash
git clone <your-repo-url> && cd data-analytics-portfolio
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python 01_sales_performance/analysis.py            # or any project
```
Each project creates realistic sample data automatically if no CSV is provided.
To use **your own data**, pass a CSV with the columns listed in that project's README:
```bash
python 02_customer_churn/analysis.py --data my_customers.csv
```
Charts and summary tables are saved in each project's `outputs/` folder.
