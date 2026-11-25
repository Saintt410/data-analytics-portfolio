"""Shared helpers for all projects."""
import argparse, os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(here, generator):
    p = argparse.ArgumentParser(); p.add_argument("--data", help="path to your CSV")
    a = p.parse_args()
    df = pd.read_csv(a.data) if a.data else generator()
    out = os.path.join(here, "outputs"); os.makedirs(out, exist_ok=True)
    return df, out

def bar(series, title, path, fmt="{:,.0f}"):
    ax = series.plot.barh(color=["#c0392b" if v < 0 else "#2a8c74" for v in series])
    ax.set_title(title); ax.invert_yaxis()
    for i, v in enumerate(series): ax.text(v, i, " " + fmt.format(v), va="center")
    plt.tight_layout(); plt.savefig(path, dpi=120); plt.close()

def section(t): print(f"\n=== {t} ===")
