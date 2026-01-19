import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import numpy as np
import pickle
from src.config import WEEKLY_DEMAND_FILE, MODELS_DIR
from src.features.timeseries_features import prepare_timeseries_data

def evaluate_model():
    """Evaluates the trained model."""
    print("Evaluating model...")
    # Load data
    try:
        data = prepare_timeseries_data()
    except Exception as e:
        print(f"Data load failed: {e}")
        return

    features = ['lag_1', 'lag_2', 'lag_4', 'rolling_mean_4', 'Month', 'WeekOfYear']
    target = 'Quantity'
    
    # Load model
    model_path = MODELS_DIR / "rf_forecast_model.pkl"
    if not model_path.exists():
        print("Model not found.")
        return
        
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        
    # Predict on all data (In real life, use hold-out set)
    y_true = data[target]
    y_pred = model.predict(data[features])
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = mean_absolute_percentage_error(y_true, y_pred)
    
    print("="*30)
    print(f"Model Performance (Training Set)")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAPE: {mape:.2%}")
    print("="*30)

if __name__ == "__main__":
    evaluate_model()
