import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from common import load, bar, section
HERE = os.path.dirname(os.path.abspath(__file__))

def generate(n_cust=4300, seed=42):
    r = np.random.default_rng(seed); rows = []; oid = 0
    for c in range(n_cust):
        k = 1 if r.random() < .66 else int(r.integers(2,15)); start = pd.Timestamp("2023-01-01") + pd.Timedelta(days=int(r.integers(0,600)))
        for j in range(k):
            d = start + pd.Timedelta(days=int(j*r.integers(10,60))); d += pd.Timedelta(hours=int(r.integers(8,22)))
            rows.append([oid, c, d, round(r.gamma(3,19.5)*(1.4 if d.month in (11,12) else 1),2)]); oid += 1
    return pd.DataFrame(rows, columns=["order_id","customer_id","order_date","amount"])

df, OUT = load(HERE, generate)
df["order_date"] = pd.to_datetime(df.order_date)
section("Business problem"); print("Most buyers never return. How do we grow repeat purchases and AOV?")
section("What the data tells me")
orders = df.groupby("order_id").amount.sum()
n = df.groupby("customer_id").order_id.nunique(); spend = df.groupby("customer_id").amount.sum()
print(f"Customers: {len(n):,} | Orders: {len(orders):,} | AOV: {orders.mean():.2f}")
print(f"Repeat rate: {(n>1).mean():.1%} | Repeat customers spend {spend[n>1].mean()/spend[n==1].mean():.1f}x more")
print("Revenue by weekday:\n", df.groupby(df.order_date.dt.day_name()).amount.sum().sort_values(ascending=False).round(0))
print("Revenue by quarter share:\n", (df.groupby(df.order_date.dt.quarter).amount.sum()/df.amount.sum()).round(3))
snap = df.order_date.max() + pd.Timedelta(days=1)
rfm = df.groupby("customer_id").agg(R=("order_date", lambda d:(snap-d.max()).days), F=("order_id","nunique"), M=("amount","sum"))
for col,asc in [("R",False),("F",True),("M",True)]:
    rfm[col+"s"] = pd.qcut(rfm[col].rank(method="first", ascending=asc), 4, labels=[1,2,3,4]).astype(int)
s = rfm.Rs+rfm.Fs+rfm.Ms
rfm["segment"] = np.select([s>=10, s>=8, s>=5], ["Champions","Loyal","At risk"], "Hibernating")
seg = (rfm.groupby("segment").M.sum()/rfm.M.sum()*100).sort_values(ascending=False); print("Revenue share % by segment:\n", seg.round(1))
rfm.to_csv(f"{OUT}/rfm_segments.csv"); bar(seg, "Revenue share % by RFM segment", f"{OUT}/rfm_segments.png", "{:.0f}%")
section("What the business should do next")
print("1. Send a second-purchase offer 14-21 days after the first order.")
print(f"2. Set a free-shipping threshold above current AOV (~{orders.mean()*1.15:.0f}) and add bundles.")
print("3. Win back 'At risk' customers with personalised offers (outputs/rfm_segments.csv).")
print("4. Concentrate promotions on peak days and Q4.")
