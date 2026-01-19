import pandas as pd
import numpy as np
from src.config import WEEKLY_DEMAND_FILE

def prepare_timeseries_data():
    """Reads weekly demand and adds lag features for ML models."""
    print("Loading weekly demand data...")
    if not WEEKLY_DEMAND_FILE.exists():
        raise FileNotFoundError(f"File not found: {WEEKLY_DEMAND_FILE}")
    
    df = pd.read_parquet(WEEKLY_DEMAND_FILE)
    
    # df has StockCode, InvoiceDate (weekly), Quantity
    # Ensure sorted
    df = df.sort_values(['StockCode', 'InvoiceDate'])
    
    print("Generating lag features...")
    # Lags: 1 week, 2 weeks, 4 weeks (1 month)
    # Rolling mean: 4 weeks
    
    # We need to process by group
    grouped = df.groupby('StockCode')
    
    df['lag_1'] = grouped['Quantity'].shift(1)
    df['lag_2'] = grouped['Quantity'].shift(2)
    df['lag_4'] = grouped['Quantity'].shift(4)
    df['rolling_mean_4'] = grouped['Quantity'].transform(lambda x: x.shift(1).rolling(window=4).mean())
    
    # Drop NaNs created by lags
    df = df.dropna()
    
    # Add date features
    df['Month'] = df['InvoiceDate'].dt.month
    df['WeekOfYear'] = df['InvoiceDate'].dt.isocalendar().week.astype(int)
    df['Year'] = df['InvoiceDate'].dt.year
    
    print(f"Features created. Rows: {len(df)}")
    return df

if __name__ == "__main__":
    try:
        df = prepare_timeseries_data()
        print(df.head())
    except Exception as e:
        print(f"Skipping execution (file likely missing): {e}")
