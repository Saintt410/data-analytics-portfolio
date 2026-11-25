import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from common import load, bar, section
HERE = os.path.dirname(os.path.abspath(__file__))

def generate(seed=42):
    r = np.random.default_rng(seed); rows = []
    prof = {"Email":(.03,.06,.03,90),"Search":(.28,.04,.049,70),"Social":(.38,.012,.02,60),"Display":(.31,.004,.006,55)}
    for ch,(share,ctr,cvr,aov) in prof.items():
        for i in range(12):
            for t in ["Prospecting","Retargeting"]:
                spend = 860000*share/24*r.uniform(.7,1.3); imp = spend*r.uniform(80,140)
                clk = imp*ctr*r.uniform(.8,1.2); conv = clk*cvr*(1.6 if t=="Retargeting" else 1)*r.uniform(.8,1.2)
                rows.append([f"{ch}-{i+1:02d}-{t[:4]}", ch, t, spend, imp, clk, conv, conv*aov*r.uniform(.9,1.1)])
    return pd.DataFrame(rows, columns=["campaign","channel","campaign_type","spend","impressions","clicks","conversions","revenue"]).round(0)

df, OUT = load(HERE, generate)
section("Business problem"); print("Where is marketing spend generating the strongest return?")
section("What the data tells me")
g = df.groupby("channel")[["spend","impressions","clicks","conversions","revenue"]].sum()
g["ctr"]=g.clicks/g.impressions; g["cvr"]=g.conversions/g.clicks; g["cpa"]=g.spend/g.conversions
g["roas"]=g.revenue/g.spend; g["budget_share"]=g.spend/g.spend.sum(); g=g.sort_values("roas", ascending=False)
pd.set_option("display.width",200); print(g.round(3))
print(f"Blended CPA: {df.spend.sum()/df.conversions.sum():.2f} | Blended ROAS: {df.revenue.sum()/df.spend.sum():.2f}x")
t = df.groupby("campaign_type")[["spend","conversions"]].sum(); t["cpa"]=t.spend/t.conversions; print(t.round(2))
c = df.assign(roas=df.revenue/df.spend).sort_values("roas"); print("Worst 5 campaigns:\n", c.head(5)[["campaign","spend","roas"]].round(2))
g.to_csv(f"{OUT}/channel_summary.csv"); bar(g.roas, "ROAS by channel", f"{OUT}/roas_by_channel.png", "{:.1f}x")
section("What the business should do next")
print(f"1. Shift budget from {g.roas.idxmin()} (ROAS {g.roas.min():.1f}x) to {g.roas.idxmax()} ({g.roas.max():.1f}x) and Search.")
print("2. Pause campaigns with ROAS below 1.0x.")
print("3. Scale retargeting, which has a lower CPA than prospecting.")
print("4. A/B test landing pages for low-conversion channels.")
