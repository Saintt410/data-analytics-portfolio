import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from common import load, bar, section
HERE = os.path.dirname(os.path.abspath(__file__))

def generate(n=1470, seed=42):
    r = np.random.default_rng(seed)
    role = r.choice(["Sales Representative","Research Scientist","Lab Technician","Manager","Sales Executive"], n)
    age = r.integers(18,60,n); ot = r.choice(["Yes","No"], n, p=[.28,.72])
    inc = (r.gamma(4,1200,n) + (role=="Manager")*8000 + (age-18)*60).round(0); sat = r.integers(1,5,n); yrs = r.integers(0,30,n)
    z = -2.2 + (ot=="Yes")*1.3 + (role=="Sales Representative")*1.1 + (age<25)*1.0 - (inc-6000)/6000*.6 - (sat-2.5)*.35 - (yrs>2)*.5
    return pd.DataFrame({"employee_id": range(n), "age": age, "department": np.where(np.char.startswith(role.astype(str),"Sales"),"Sales","R&D"),
        "job_role": role, "overtime": ot, "monthly_income": inc, "job_satisfaction": sat, "years_at_company": yrs,
        "attrition": (r.random(n) < 1/(1+np.exp(-z))).astype(int)})

df, OUT = load(HERE, generate)
section("Business problem"); print("Turnover is costly. Which factors are linked to higher attrition?")
section("What the data tells me")
print(f"Attrition rate: {df.attrition.mean():.1%} ({df.attrition.sum()} leavers)")
print(f"Estimated cost (50% of annual salary per leaver): {(df.loc[df.attrition==1,'monthly_income']*12*.5).sum():,.0f}")
for col in ["overtime","job_role","job_satisfaction","department"]:
    print(df.groupby(col).attrition.mean().sort_values(ascending=False).round(3), "\n")
print(df.groupby(pd.cut(df.age,[17,25,35,45,60]), observed=True).attrition.mean().round(3))
print(df.groupby(pd.cut(df.monthly_income,[0,3000,6000,10000,1e6]), observed=True).attrition.mean().round(3))
print(df.groupby(pd.cut(df.years_at_company,[-1,2,5,10,40]), observed=True).attrition.mean().round(3))
X = pd.get_dummies(df[["overtime","age","monthly_income","job_satisfaction","years_at_company","job_role"]], drop_first=True).astype(float)
m = LogisticRegression(max_iter=2000).fit(StandardScaler().fit_transform(X), df.attrition)
coef = pd.Series(m.coef_[0], X.columns).sort_values(ascending=False); print("Factor strength (+ = more attrition):\n", coef.round(2))
bar(coef, "Attrition drivers (standardised coefficients)", f"{OUT}/attrition_drivers.png", "{:.2f}")
section("What the business should do next")
print("1. Audit and cap overtime; hire to cover workload gaps.")
print("2. Review pay bands for junior and sales roles.")
print("3. Mentoring and stay-interviews for employees in years 0-2.")
print("4. Track job satisfaction quarterly and act on low scores.")
