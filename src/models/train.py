import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from src.features.timeseries_features import prepare_timeseries_data
from src.config import MODELS_DIR

def train_model():
    """Trains a Random Forest model for demand forecasting."""
    print("Preparing data...")
    try:
        data = prepare_timeseries_data()
    except Exception as e:
        print(f"Data preparation failed: {e}")
        return

    # Select Top Products to save time/complexity for this demo?
    # Or train one global model (Machine Learning approach often works well with global models + product embeddings/IDs)
    # Simple approach: Global model with StockCode usage? StockCode is categorical with high cardinality.
    # Better: Train for a few top items or use only general time features + lag features (ignoring product ID specific nuances except via lags).
    # Let's keep StockCode out of features for simplicity, or target encoding.
    # Lags capture the product specific level.
    
    features = ['lag_1', 'lag_2', 'lag_4', 'rolling_mean_4', 'Month', 'WeekOfYear']
    target = 'Quantity'
    
    print(f"Training on {len(data)} rows using features: {features}")
    
    X = data[features]
    y = data[target]
    
    # Time Series Split
    tscv = TimeSeriesSplit(n_splits=3)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    
    fold = 1
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        print(f"Fold {fold} MAE: {mae:.2f}")
        fold += 1
        
    # Final Fit on all data
    print("Retraining on full dataset...")
    model.fit(X, y)
    
    # Save model
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / "rf_forecast_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
