import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from common import load, bar, section
HERE = os.path.dirname(os.path.abspath(__file__))

def generate(n=7000, seed=42):
    r = np.random.default_rng(seed)
    contract = r.choice(["Month-to-month","One year","Two year"], n, p=[.55,.21,.24])
    tenure = r.integers(1,73,n); pay = r.choice(["Electronic check","Credit card","Bank transfer","Mailed check"], n)
    charges = r.uniform(20,115,n).round(2); support = r.choice(["Yes","No"], n)
    z = -1.2 + (contract=="Month-to-month")*1.6 - (contract=="Two year")*1.8 - tenure*.035 \
        + (pay=="Electronic check")*.6 + (charges-65)*.012 + (support=="No")*.5
    return pd.DataFrame({"customer_id": range(n), "tenure": tenure, "contract": contract, "payment_method": pay,
        "monthly_charges": charges, "tech_support": support, "churn": (r.random(n) < 1/(1+np.exp(-z))).astype(int)})

df, OUT = load(HERE, generate)
section("Business problem"); print("Customers are leaving. Why, and who is most at risk?")
section("What the data tells me")
print(f"Churn rate: {df.churn.mean():.1%}")
print(f"Monthly revenue at risk: {df.loc[df.churn==1,'monthly_charges'].sum():,.0f}")
by_c = df.groupby("contract").churn.mean().sort_values(ascending=False); print(by_c.round(3))
print(df.groupby(pd.cut(df.tenure,[0,6,12,24,72]), observed=True).churn.mean().round(3))
print(df.groupby("payment_method").churn.mean().sort_values(ascending=False).round(3))
print(df.groupby("tech_support").churn.mean().round(3))
X = pd.get_dummies(df.drop(columns=["customer_id","churn"]), drop_first=True)
Xtr,Xte,ytr,yte = train_test_split(X, df.churn, test_size=.2, random_state=42, stratify=df.churn)
m = RandomForestClassifier(300, random_state=42, min_samples_leaf=5).fit(Xtr,ytr)
print(f"Model AUC: {roc_auc_score(yte, m.predict_proba(Xte)[:,1]):.2f}")
imp = pd.Series(m.feature_importances_, X.columns).nlargest(8); print("Top drivers:\n", imp.round(3))
df["risk"] = m.predict_proba(X)[:,1]; df.sort_values("risk", ascending=False).head(500).to_csv(f"{OUT}/top_500_at_risk.csv", index=False)
bar(by_c*100, "Churn % by contract", f"{OUT}/churn_by_contract.png", "{:.1f}%")
section("What the business should do next")
print("1. Offer discounts to move month-to-month customers onto annual contracts.")
print("2. Build a 90-day onboarding journey (churn is highest in first 6 months).")
print("3. Bundle tech support and push auto-pay instead of electronic check.")
print("4. Contact the top 500 at-risk customers (outputs/top_500_at_risk.csv).")
