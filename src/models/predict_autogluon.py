"""
AutoGluon Prediction Script
Generate forecasts for next 4 weeks
"""
import pandas as pd
from pathlib import Path
from autogluon.timeseries import TimeSeriesPredictor
from src.config import MODELS_DIR, FORECAST_OUTPUTS_DIR, WEEKLY_DEMAND_FILE

def predict_with_autogluon():
    """Generate forecasts using AutoGluon model"""
    print("Loading AutoGluon model...")
    
    # Load model
    predictor = TimeSeriesPredictor.load(str(MODELS_DIR / "autogluon_forecast"))
    
    # Load latest data
    print("Loading latest data...")
    df = pd.read_parquet(WEEKLY_DEMAND_FILE)
    
    # Prepare for prediction
    df_ag = df.rename(columns={
        'StockCode': 'item_id',
        'InvoiceDate': 'timestamp',
        'Quantity': 'target'
    })
    
    from autogluon.timeseries import TimeSeriesDataFrame
    ts_df = TimeSeriesDataFrame.from_data_frame(
        df_ag,
        id_column='item_id',
        timestamp_column='timestamp'
    )
    
    # Generate predictions (point forecast only)
    print("Generating forecasts for next 4 weeks...")
    predictions = predictor.predict(ts_df)
    
    # Convert to DataFrame - AutoGluon returns multi-index with item_id and timestamp
    forecast_df = predictions.reset_index()
    
    # Check actual columns
    print(f"Prediction columns: {forecast_df.columns.tolist()}")
    
    # Rename columns based on actual structure
    # AutoGluon typically returns: item_id, timestamp, mean (and possibly other quantiles)
    if 'item_id' in forecast_df.columns:
        forecast_df = forecast_df.rename(columns={
            'item_id': 'StockCode',
            'timestamp': 'Forecast_Week'
        })
    
    # Find the forecast column (usually 'mean' or first numeric column)
    numeric_cols = forecast_df.select_dtypes(include=['float64', 'int64']).columns
    if 'mean' in forecast_df.columns:
        forecast_df = forecast_df.rename(columns={'mean': 'Forecast_Qty'})
    elif len(numeric_cols) > 0:
        # Use first numeric column as forecast
        forecast_df = forecast_df.rename(columns={numeric_cols[0]: 'Forecast_Qty'})
    
    # Keep only needed columns
    cols_to_keep = ['StockCode', 'Forecast_Week', 'Forecast_Qty']
    forecast_df = forecast_df[cols_to_keep]
    
    # Add estimated confidence intervals (±20% as approximation)
    forecast_df['Lower_Bound'] = forecast_df['Forecast_Qty'] * 0.8
    forecast_df['Upper_Bound'] = forecast_df['Forecast_Qty'] * 1.2
    
    # Save results
    FORECAST_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FORECAST_OUTPUTS_DIR / "demand_forecast_autogluon.csv"
    forecast_df.to_csv(output_path, index=False)
    
    print(f"\n✅ Forecasts saved to: {output_path}")
    print(f"📊 Total products forecasted: {forecast_df['StockCode'].nunique()}")
    print(f"📅 Forecast horizon: 4 weeks")
    print("\nSample forecasts:")
    print(forecast_df.head(10))
    
    return forecast_df

if __name__ == "__main__":
    try:
        forecast_df = predict_with_autogluon()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
