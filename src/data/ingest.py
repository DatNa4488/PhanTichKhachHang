import pandas as pd
import sys
from src.config import RAW_DATA_FILE, RAW_DATA_DIR

def load_excel_data():
    """Reads the raw Excel file."""
    print(f"Loading data from {RAW_DATA_FILE}...")
    if not RAW_DATA_FILE.exists():
        raise FileNotFoundError(f"File not found: {RAW_DATA_FILE}")
    
    # Read Excel - this might take a moment
    df = pd.read_excel(RAW_DATA_FILE)
    print(f"Loaded {len(df)} rows.")
    return df

def ingest_data():
    """Loads raw data and saves as parquet for faster access."""
    df = load_excel_data()
    
    # Enforce types to avoid pyarrow errors
    print("Enforcing column types...")
    # InvoiceNo can be int or string (if C prefix). Convert to string.
    df['InvoiceNo'] = df['InvoiceNo'].astype(str)
    # StockCode can be mixed.
    df['StockCode'] = df['StockCode'].astype(str)
    # CustomerID is float (with NaNs). Leave as is or convert to object?
    # Pyarrow handles float with NaN fine.
    
    # Description is object.
    df['Description'] = df['Description'].astype(str)
    
    # Country is object.
    df['Country'] = df['Country'].astype(str)

    # Save to intermediate raw parquet
    output_path = RAW_DATA_DIR / "online_retail_raw.parquet"
    print(f"Saving raw parquet to {output_path}...")
    try:
        df.to_parquet(output_path, index=False)
    except Exception as e:
        print(f"Parquet save failed: {e}")
        # Fallback to CSV if parquet fails
        csv_path = RAW_DATA_DIR / "online_retail_raw.csv"
        print(f"Falling back to CSV: {csv_path}")
        df.to_csv(csv_path, index=False)
        
    print("Ingestion complete.")

if __name__ == "__main__":
    try:
        ingest_data()
    except Exception as e:
        print(f"Error during ingestion: {e}")
        sys.exit(1)
