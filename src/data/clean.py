import pandas as pd
import sys
from src.config import RAW_DATA_DIR, CLEAN_SALES_FILE

def clean_data():
    """Reads raw parquet, cleans it, and saves to processed."""
    input_path = RAW_DATA_DIR / "online_retail_raw.parquet"
    
    print(f"Loading raw data from {input_path}...")
    if not input_path.exists():
        raise FileNotFoundError(f"Raw data not found at {input_path}. Run ingest.py first.")
    
    df = pd.read_parquet(input_path)
    initial_rows = len(df)
    
    # 1. Drop missing CustomerID
    print("Dropping missing CustomerID...")
    df = df.dropna(subset=['CustomerID'])
    
    # 2. Convert CustomerID to int
    df['CustomerID'] = df['CustomerID'].astype(int)
    
    # 3. Handle Canceled orders (InvoiceNo starts with 'C')
    # We will exclude them for demand forecasting of "net sales", 
    # but analysis might want them. For this project, we prioritize demand, so we remove cancellations.
    print(" removing cancellations...")
    df['InvoiceNo'] = df['InvoiceNo'].astype(str)
    df = df[~df['InvoiceNo'].str.startswith('C')]
    
    # 4. Filter non-positive Quantity and Price
    print("Filtering invalid Quantity and Price...")
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    
    # 5. Convert InvoiceDate to datetime if not already
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # 6. Calculate TotalValue
    df['TotalValue'] = df['Quantity'] * df['UnitPrice']
    
    final_rows = len(df)
    print(f"Data cleaned. Rows: {initial_rows} -> {final_rows} (Removed {initial_rows - final_rows})")
    
    # Save
    print(f"Saving cleaned data to {CLEAN_SALES_FILE}...")
    CLEAN_SALES_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CLEAN_SALES_FILE, index=False)
    print("Cleaning complete.")

if __name__ == "__main__":
    clean_data()
