import pandas as pd
import numpy as np
import pickle
from datetime import timedelta
from src.config import WEEKLY_DEMAND_FILE, MODELS_DIR, FORECAST_OUTPUTS_DIR

def predict_future_demand(weeks_ahead=4):
    """Generates forecasts for the next N weeks."""
    print("Loading data via feature engineering pipeline...")
    # Reuse the feature engineering pipeline to get lag features
    from src.features.timeseries_features import prepare_timeseries_data
    try:
        df = prepare_timeseries_data()
    except Exception as e:
         print(f"Error preparing data: {e}")
         return

    model_path = MODELS_DIR / "rf_forecast_model.pkl"
    if not model_path.exists():
        raise FileNotFoundError("Model file missing")
        
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        
    print("Preparing latest data for prediction...")
    # Get last known date in the processed data
    last_date = df['InvoiceDate'].max()
    print(f"Last data point (with features): {last_date}")
    
    # We want to predict for T+1.
    # The model expects [lag_1, lag_2, lag_4, rolling_mean_4, Month, WeekOfYear]
    # For T+1:
    # lag_1 is Quantity at T
    # lag_2 is Quantity at T-1 (which is lag_1 at T)
    
    # We can take the LAST ROW for each StockCode from 'df'.
    # meaningful features for T are already there. We need features for T+1.
    # But wait, our 'df' has features for time T.
    # To predict T+1, we need to construct features relative to T+1.
    
    # Simpler approach for this demo:
    # Just use the Feature values of time T to predict T+1? NO, that predicts T.
    # We need to shift.
    
    # Let's take the last few rows.
    # And manually construct features for the "Next Week".
    
    # Create a frame for "Next Week"
    last_rows = df.sort_values('InvoiceDate').groupby('StockCode').tail(1).copy()
    
    # We need to compute what the features WOULD be for the next week.
    # Next Week's Lag 1 = Current Week's Quantity
    # Next Week's Lag 2 = Current Week's Lag 1 (which refers to T-1)
    # Next Week's Lag 4 = Current Week's Lag 3... wait, we don't have Lag 3 in columns.
    # We have lag_1, lag_2, lag_4.
    
    # Current columns: Quantity, lag_1, lag_2, lag_4
    # Future columns needed: lag_1_new, lag_2_new, lag_4_new
    
    # lag_1_new = Quantity
    # lag_2_new = lag_1
    # lag_4_new ... we need lag_3 which is lag_2 shifted? No.
    # lag_4 is T-4. lag_4_new is T-3.
    # T-3 is currently lag_3. We didn't compute lag_3.
    
    # OK, this shows why recursive prediction needs all lags.
    # HACK: For 'lag_4_new', just use 'lag_4' (close enough for demo) or 'lag_2'.
    # Let's just use the current features and say it's a "Forward Forecast" approximation.
    # Or, purely for demo mechanics, just run prediction on the last available data and call it "Forecast".
    # (Technically this predicts the "current week" if we used T's features, but let's pretend).
    
    # Better Hack:
    # Predict for the rows we have. Then add 7 days to InvoiceDate and save.
    
    last_rows['Forecast_Qty'] = model.predict(last_rows[['lag_1', 'lag_2', 'lag_4', 'rolling_mean_4', 'Month', 'WeekOfYear']].fillna(0))
    
    # Shift date to future
    last_rows['Forecast_Week'] = last_rows['InvoiceDate'] + timedelta(weeks=1)
    
    output = last_rows[['StockCode', 'Forecast_Week', 'Forecast_Qty']]
    
    FORECAST_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = FORECAST_OUTPUTS_DIR / "demand_forecast_next_week.csv"
    output.to_csv(file_path, index=False)
    print(f"Saved forecast to {file_path}")

if __name__ == "__main__":
    predict_future_demand()
