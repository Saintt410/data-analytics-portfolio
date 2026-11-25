"""Business Analytics Toolkit - upload your CSV and get answers. Run: streamlit run streamlit_app.py"""
import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Business Analytics Toolkit", layout="wide")
st.title("Business Analytics Toolkit")
st.write("Pick an analysis, upload your company's CSV (or use the sample), and get the business problem, "
         "what the data says, and what to do next. Nothing is stored.")

yes = lambda s: s.astype(str).str.lower().isin(["yes", "1", "true", "y"])
money = lambda v: f"${v:,.0f}"

SAMPLES = {
 "Sales Performance": "region,category,sku,customer_id,revenue,profit\nWest,Technology,T-100,C1,1200,300\nEast,Furniture,F-200,C2,800,-50\nCentral,Furniture,F-201,C3,950,-120\nWest,Office,O-300,C1,300,90\nSouth,Technology,T-101,C4,1500,420\nEast,Technology,T-102,C5,1100,260",
 "Customer Churn": "customer_id,contract,tenure,monthly_charges,churn\n1,Month-to-month,2,70,Yes\n2,One year,24,60,No\n3,Two year,50,80,No\n4,Month-to-month,5,90,Yes\n5,Month-to-month,30,55,No\n6,One year,12,65,Yes",
 "Marketing Campaigns": "channel,spend,clicks,impressions,conversions,revenue\nEmail,5000,4000,50000,400,39000\nSearch,20000,15000,300000,700,92000\nSocial,15000,9000,400000,250,36000\nDisplay,25000,6000,900000,40,27000",
 "E-commerce Customers": "order_id,customer_id,amount\n1,A,50\n2,A,70\n3,B,40\n4,C,120\n5,C,60\n6,D,30\n7,C,45",
 "Employee Attrition": "employee_id,overtime,job_role,age,monthly_income,attrition\n1,Yes,Sales Representative,23,2500,Yes\n2,No,Manager,45,12000,No\n3,Yes,Lab Technician,29,3200,Yes\n4,No,Research Scientist,35,5000,No\n5,No,Sales Executive,40,7000,No\n6,Yes,Sales Representative,26,2800,No",
}
PROBLEMS = {
 "Sales Performance": "What is driving growth, and where is the business losing money?",
 "Customer Churn": "Why are customers leaving, and who is most at risk?",
 "Marketing Campaigns": "Which channels generate the strongest return on spend?",
 "E-commerce Customers": "How do customers buy, and how can we grow repeat purchases and order value?",
 "Employee Attrition": "Which factors are linked to higher employee turnover?",
}

def sales(df):
    rev, prof = df.revenue.sum(), df.profit.sum()
    reg = df.groupby("region").profit.sum().sort_values(ascending=False)
    cat = df.groupby("category").revenue.sum().sort_values(ascending=False)
    loss = df.groupby("sku").profit.sum().loc[lambda s: s < 0]
    cust = df.groupby("customer_id").revenue.sum().sort_values(ascending=False)
    top = cust.head(max(1, round(len(cust) * .2))).sum() / rev
    kpis = {"Revenue": money(rev), "Profit": money(prof), "Margin": f"{prof/rev:.1%}", "Loss-making SKUs": len(loss)}
    f = [f"{cat.index[0]} is the top category ({cat.iloc[0]/rev:.0%} of revenue).",
         f"{reg.index[0]} is most profitable; {reg.index[-1]} is weakest ({money(reg.iloc[-1])}).",
         f"Top 20% of customers bring {top:.0%} of revenue.", f"{len(loss)} SKUs lose money."]
    a = [f"Review discounts and costs in {reg.index[-1]}.", "Reprice or delist loss-making SKUs.", "Start a key-account program for top customers."]
    return kpis, "Profit by region", reg, f, a

def churn(df):
    df["c"] = yes(df.churn); rate = df.c.mean()
    by = df.groupby("contract").c.mean().sort_values(ascending=False)
    early = df[df.tenure <= 6].c.mean() if (df.tenure <= 6).any() else 0
    lost = df[df.c].monthly_charges.sum() * 12
    kpis = {"Customers": len(df), "Churn rate": f"{rate:.1%}", "First-6-month churn": f"{early:.1%}", "Revenue lost / yr": money(lost)}
    f = [f"{rate:.1%} of customers churned.", f"{by.index[0]} churns most ({by.iloc[0]:.0%}).",
         f"New customers (≤6 months) churn at {early:.0%}.", f"Churn costs about {money(lost)} a year."]
    a = [f"Offer incentives to move {by.index[0]} customers to longer plans.", "Build a 90-day onboarding journey.", "Contact high-bill, short-tenure customers early."]
    return kpis, "Churn rate by contract", by * 100, f, a

def marketing(df):
    g = df.groupby("channel")[["spend", "clicks", "conversions", "revenue"]].sum()
    g["roas"] = g.revenue / g.spend; g = g.sort_values("roas", ascending=False)
    sp, cv = g.spend.sum(), g.conversions.sum()
    kpis = {"Spend": money(sp), "Conversions": int(cv), "CPA": money(sp / cv), "ROAS": f"{g.revenue.sum()/sp:.1f}x"}
    b, w = g.index[0], g.index[-1]
    f = [f"{b} has the best ROAS ({g.roas[b]:.1f}x) on {g.spend[b]/sp:.0%} of budget.",
         f"{w} has the weakest ROAS ({g.roas[w]:.1f}x) on {g.spend[w]/sp:.0%} of budget."]
    a = [f"Shift budget from {w} to {b}.", "A/B test landing pages on weak channels.", "Review channel results monthly."]
    return kpis, "ROAS by channel", g.roas, f, a

def ecommerce(df):
    aov = df.groupby("order_id").amount.sum().mean()
    c = df.groupby("customer_id").agg(orders=("order_id", "nunique"), spend=("amount", "sum"))
    rr = (c.orders > 1).mean()
    ratio = c[c.orders > 1].spend.mean() / max(c[c.orders == 1].spend.mean(), 1)
    kpis = {"Customers": len(c), "AOV": money(aov), "Repeat rate": f"{rr:.0%}", "Revenue": money(df.amount.sum())}
    dist = c.orders.clip(upper=3).value_counts().sort_index().rename({1: "1 order", 2: "2 orders", 3: "3+ orders"})
    f = [f"{rr:.0%} of customers buy more than once.", f"Repeat customers spend {ratio:.1f}x more.", f"Average order value is {money(aov)}."]
    a = ["Send a second-purchase offer 2–3 weeks after first order.", f"Set a free-shipping threshold near {money(aov*1.15)}.", "Win back inactive customers."]
    return kpis, "Customers by number of orders", dist, f, a

def attrition(df):
    df["l"] = yes(df.attrition); df["ot"] = yes(df.overtime)
    ot, no = df[df.ot].l.mean(), df[~df.ot].l.mean()
    roles = df.groupby("job_role").l.mean().sort_values(ascending=False)
    kpis = {"Employees": len(df), "Attrition": f"{df.l.mean():.1%}", "Overtime attrition": f"{ot:.0%}", "No-overtime attrition": f"{no:.0%}"}
    f = [f"Overall attrition is {df.l.mean():.1%}.", f"Overtime staff leave at {ot:.0%} vs {no:.0%}.",
         f"{roles.index[0]} has the highest attrition ({roles.iloc[0]:.0%}).",
         f"Under-25s: {df[df.age < 25].l.mean():.0%}; income under $3K: {df[df.monthly_income < 3000].l.mean():.0%}."]
    a = ["Audit and reduce overtime.", f"Review pay and workload for {roles.index[0]}.", "Add mentoring and stay-interviews for early-career staff."]
    return kpis, "Attrition rate by job role (%)", roles * 100, f, a

RUN = {"Sales Performance": sales, "Customer Churn": churn, "Marketing Campaigns": marketing,
       "E-commerce Customers": ecommerce, "Employee Attrition": attrition}

choice = st.sidebar.radio("Analysis", list(RUN))
st.sidebar.markdown("---\nBuilt with Python, pandas and Streamlit")
sample = SAMPLES[choice]
cols = sample.splitlines()[0]
st.header(choice)
st.caption(f"Required columns: `{cols}`")
st.download_button("Download template CSV", sample, f"{choice.lower().replace(' ', '_')}_template.csv")
up = st.file_uploader("Upload a CSV file", type="csv")
if up is None:
    st.info("No file uploaded — showing the sample file.")
df = pd.read_csv(up if up else io.StringIO(sample))
df.columns = df.columns.str.strip().str.lower()
missing = [c for c in cols.split(",") if c not in df.columns]
if missing:
    st.error(f"Missing columns: {', '.join(missing)}"); st.stop()

with st.expander("Your data", expanded=False):
    st.dataframe(df, use_container_width=True)
try:
    kpis, title, series, findings, actions = RUN[choice](df.copy())
except Exception as e:
    st.error(f"Could not analyze this file: {e}"); st.stop()

for col, (k, v) in zip(st.columns(len(kpis)), kpis.items()):
    col.metric(k, v)
st.subheader("What is the business problem?"); st.write(PROBLEMS[choice])
st.subheader(title); st.bar_chart(series)
c1, c2 = st.columns(2)
c1.subheader("What does the data tell me?"); c1.markdown("\n".join(f"- {x}" for x in findings))
c2.subheader("What should the business do next?"); c2.markdown("\n".join(f"{i}. {x}" for i, x in enumerate(actions, 1)))
