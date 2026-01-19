import pandas as pd
from src.config import CLEAN_SALES_FILE, CUSTOMER_TRANSACTIONS_FILE, WEEKLY_DEMAND_FILE

def build_marts():
    """Aggregates cleaned data into analytics tables."""
    print("Loading clean sales data...")
    if not CLEAN_SALES_FILE.exists():
        raise FileNotFoundError(f"Clean sales file not found: {CLEAN_SALES_FILE}")
    
    df = pd.read_parquet(CLEAN_SALES_FILE)
    
    # --- 1. Customer Transactions Mart (for RFM) ---
    print("Building customer transactions mart...")
    # Group by CustomerID
    # Recency: Max invoice date (we'll calculate 'days since' in rfm.py or here)
    # Frequency: Count of unique InvoiceNo
    # Monetary: Sum of TotalValue
    
    customer_mart = df.group_by('CustomerID').agg({
        'InvoiceDate': 'max',
        'InvoiceNo': 'nunique',
        'TotalValue': 'sum'
    }).rename(columns={
        'InvoiceDate': 'LastPurchaseDate',
        'InvoiceNo': 'Frequency',
        'TotalValue': 'Monetary'
    }).reset_index()
    
    print(f"Customer Mart: {len(customer_mart)} customers.")
    customer_mart.to_parquet(CUSTOMER_TRANSACTIONS_FILE, index=False)
    
    # --- 2. Weekly Demand Mart (for Forecasting) ---
    print("Building weekly demand mart...")
    # We need a complete time series for each product, but for now let's just sum up.
    # We will handle gaps (zero sales) in the features step or here.
    # It's better to handle gaps here to have a "clean" demand time series.
    
    # Filter for top products? Or all? Let's do all for now, but aggregation might be huge.
    # There are many StockCodes.
    
    # Resample to weekly
    # Set index to Date
    df_ts = df.set_index('InvoiceDate')
    
    # Group by StockCode and resample. 
    # This is a bit tricky with multiple groups.
    # Easier: Group by StockCode + Grouper(freq='W-MON')
    
    weekly_demand = df_ts.groupby(['StockCode', pd.Grouper(freq='W-MON')])['Quantity'].sum().reset_index()
    
    print(f"Weekly Demand Mart: {len(weekly_demand)} rows.")
    weekly_demand.to_parquet(WEEKLY_DEMAND_FILE, index=False)
    print("Marts built successfully.")

if __name__ == "__main__":
    # Pandas < 2.0 might not support group_by standard, use groupby
    if not hasattr(pd.DataFrame, 'group_by'):
        pd.DataFrame.group_by = pd.DataFrame.groupby
        
    build_marts()
