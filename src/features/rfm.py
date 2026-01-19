import pandas as pd
import numpy as np
from src.config import CUSTOMER_TRANSACTIONS_FILE, CUSTOMER_SEGMENTS_FILE

def calculate_rfm_segments():
    """Calculates RFM scores and segments customers."""
    print("Loading customer transactions...")
    if not CUSTOMER_TRANSACTIONS_FILE.exists():
        raise FileNotFoundError(f"File not found: {CUSTOMER_TRANSACTIONS_FILE}")
    
    df = pd.read_parquet(CUSTOMER_TRANSACTIONS_FILE)
    
    # Ensure datatypes
    df['LastPurchaseDate'] = pd.to_datetime(df['LastPurchaseDate'])
    
    # Calculate Recency (days since last purchase relative to max date in dataset)
    # In a real scenario, we might use 'today', but for historical data, max date is better.
    max_date = df['LastPurchaseDate'].max()
    df['Recency'] = (max_date - df['LastPurchaseDate']).dt.days
    
    # Rename for clarity
    # df columns are: CustomerID, LastPurchaseDate, Frequency, Monetary
    
    # Calculate RFM Scores (1-4, 4 being best)
    # Recency: Lower is better -> Labels 4,3,2,1
    # Frequency: Higher is better -> Labels 1,2,3,4
    # Monetary: Higher is better -> Labels 1,2,3,4
    
    # Using qcut
    print("Calculating RFM scores...")
    try:
        df['R_Score'] = pd.qcut(df['Recency'], 4, labels=[4, 3, 2, 1])
        df['F_Score'] = pd.qcut(df['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4]) # Rank to handle ties
        df['M_Score'] = pd.qcut(df['Monetary'], 4, labels=[1, 2, 3, 4])
    except Exception as e:
        print(f"Error in qcut: {e}. Falling back to manual check or ranking.")
        # Fallback if validation fails (e.g. too few unique values)
        df['R_Score'] = pd.cut(df['Recency'].rank(pct=True), bins=[0, 0.25, 0.5, 0.75, 1], labels=[4, 3, 2, 1], include_lowest=True)
        df['F_Score'] = pd.cut(df['Frequency'].rank(pct=True), bins=[0, 0.25, 0.5, 0.75, 1], labels=[1, 2, 3, 4], include_lowest=True)
        df['M_Score'] = pd.cut(df['Monetary'].rank(pct=True), bins=[0, 0.25, 0.5, 0.75, 1], labels=[1, 2, 3, 4], include_lowest=True)

    # Combine RFM
    df['RFM_Score'] = df['R_Score'].astype(str) + df['F_Score'].astype(str) + df['M_Score'].astype(str)
    
    # Segment Map
    # Simple Segmentation Logic based on scores
    def segment_customer(row):
        r = int(row['R_Score'])
        f = int(row['F_Score'])
        m = int(row['M_Score'])
        fm = (f + m) / 2
        
        if r >= 4 and fm >= 4:
            return 'Champions (Khách Hàng VIP)'
        elif r >= 3 and fm >= 3:
            return 'Loyal Customers (Khách Hàng Trung Thành)'
        elif r >= 3 and fm >= 1:
            return 'Potential Loyalist (Khách Hàng Tiềm Năng)'
        elif r >= 2 and fm >= 2:
            return 'At Risk (Nguy Cơ Rời Bỏ)'
        elif r <= 1 and fm >= 3:
            return 'Can\'t Lose Them (Không Thể Mất)' # High value but lost
        elif r <= 2 and fm <= 2:
            return 'Hibernating (Ngủ Đông)'
        else:
            return 'About to Sleep (Sắp Rời Bỏ)'

    df['Segment'] = df.apply(segment_customer, axis=1)
    
    print("Segmentation complete. Distribution:")
    print(df['Segment'].value_counts())
    
    print(f"Saving segments to {CUSTOMER_SEGMENTS_FILE}...")
    df.to_parquet(CUSTOMER_SEGMENTS_FILE, index=False)

if __name__ == "__main__":
    calculate_rfm_segments()
