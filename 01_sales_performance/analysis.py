import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from common import load, bar, section
HERE = os.path.dirname(os.path.abspath(__file__))

def generate(n=10000, seed=42):
    r = np.random.default_rng(seed)
    region = r.choice(["West","East","South","Central"], n, p=[.32,.28,.22,.18])
    cat = r.choice(["Technology","Furniture","Office Supplies"], n, p=[.35,.3,.35])
    rev = r.gamma(2, 230, n) * np.where(cat=="Technology", 1.6, 1)
    disc = np.clip(r.normal(.12,.08,n) + np.where((region=="Central")&(cat=="Furniture"), .2, 0), 0, .7)
    margin = np.where(cat=="Technology", .38, np.where(cat=="Furniture", .22, .3)) - disc*1.1
    return pd.DataFrame({"order_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(r.integers(0,730,n), "D"),
        "customer_id": r.integers(1,800,n), "region": region, "category": cat,
        "sku": [f"{c[:3].upper()}-{i}" for c,i in zip(cat, r.integers(1,60,n))],
        "revenue": rev.round(2), "discount": disc.round(2), "profit": (rev*margin).round(2)})

df, OUT = load(HERE, generate)
df["order_date"] = pd.to_datetime(df.order_date); df["year"] = df.order_date.dt.year
section("Business problem"); print("Revenue grows but margins are flat. Where is profit made and lost?")
section("What the data tells me")
yr = df.groupby("year").revenue.sum(); print("Revenue by year:\n", yr.round(0)); print("Growth:", f"{yr.pct_change().iloc[-1]:.1%}")
print("Gross margin:", f"{df.profit.sum()/df.revenue.sum():.1%}")
reg = df.groupby("region")[["revenue","profit"]].sum().sort_values("profit", ascending=False); print(reg.round(0))
cat = df.groupby("category")[["revenue","profit"]].sum(); print(cat.round(0))
sku = df.groupby("sku").profit.sum(); loss = sku[sku<0]; print(f"Loss-making SKUs: {len(loss)} (total {loss.sum():,.0f})")
c = df.groupby("customer_id").revenue.sum().sort_values(ascending=False)
print(f"Top 20% customers = {c.head(int(len(c)*.2)).sum()/c.sum():.0%} of revenue")
df["disc_band"] = pd.cut(df.discount, [-.01,.1,.2,.3,1], labels=["0-10%","10-20%","20-30%","30%+"])
print(df.groupby("disc_band", observed=True).profit.mean().round(1))
bar(reg.profit, "Profit by region", f"{OUT}/profit_by_region.png")
section("What the business should do next")
worst = reg.profit.idxmin()
print(f"1. Cap discounts at 20% (orders above 30% average {df[df.discount>.3].profit.mean():,.0f} profit).")
print(f"2. Fix the weakest region: {worst}.")
print(f"3. Reprice or delist the {len(loss)} loss-making SKUs.")
print("4. Launch a key-account program for the top 20% of customers.")
