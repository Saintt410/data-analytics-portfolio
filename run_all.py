"""Run every project in one go: python run_all.py"""
import subprocess, sys, glob
for f in sorted(glob.glob("0*/analysis.py")):
    print(f"\n\n######## {f} ########"); subprocess.run([sys.executable, f], check=True)
