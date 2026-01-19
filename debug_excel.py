import pandas as pd
import traceback
import os

print(f"CWD: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

try:
    print("Attempting to read excel...")
    df = pd.read_excel("Online Retail.xlsx", nrows=10)
    print("Success reading 10 rows")
    print(df.columns)
except Exception:
    print("Error reading excel:")
    traceback.print_exc()
