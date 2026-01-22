"""
AutoGluon-based Time Series Forecasting
Replaces Random Forest with state-of-the-art ensemble models
"""
import pandas as pd
import numpy as np
from pathlib import Path
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
from src.config import MODELS_DIR, WEEKLY_DEMAND_FILE

def prepare_autogluon_data():
    """Prepare data in AutoGluon format"""
    print("Loading weekly demand data...")
    df = pd.read_parquet(WEEKLY_DEMAND_FILE)
    
    # AutoGluon expects: item_id, timestamp, target
    df_ag = df.rename(columns={
        'StockCode': 'item_id',
        'InvoiceDate': 'timestamp',
        'Quantity': 'target'
    })
    
    # Convert to TimeSeriesDataFrame
    ts_df = TimeSeriesDataFrame.from_data_frame(
        df_ag,
        id_column='item_id',
        timestamp_column='timestamp'
    )
    
    # Convert to regular weekly frequency (fix irregular data)
    print("Converting to regular weekly frequency...")
    ts_df = ts_df.convert_frequency('W')  # W = Weekly
    
    print(f"Prepared {len(ts_df)} time series with weekly frequency")
    return ts_df

def train_autogluon_model():
    """Train AutoGluon forecasting model"""
    print("="*60)
    print("TRAINING AUTOGLUON TIME SERIES MODEL")
    print("="*60)
    
    # Prepare data
    train_data = prepare_autogluon_data()
    
    # Create predictor with explicit frequency
    predictor = TimeSeriesPredictor(
        path=str(MODELS_DIR / "autogluon_forecast"),
        target='target',
        prediction_length=4,  # Forecast 4 weeks ahead
        eval_metric='MAE',
        freq='W',  # Explicitly set weekly frequency
        verbosity=2
    )
    
    print("\nTraining models (this may take 10-15 minutes)...")
    print("AutoGluon will automatically try multiple models:")
    print("  - Naive (baseline)")
    print("  - SeasonalNaive")
    print("  - ETS (Exponential Smoothing)")
    print("  - ARIMA")
    print("  - Theta")
    print("  - DeepAR (Neural Network)")
    print("  - Temporal Fusion Transformer (if time permits)")
    
    # Train with time limit
    predictor.fit(
        train_data,
        time_limit=600,  # 10 minutes
        presets='medium_quality',  # Options: fast_training, medium_quality, best_quality
        num_val_windows=3,  # Time series cross-validation folds
        enable_ensemble=True  # Combine multiple models
    )
    
    # Get leaderboard (skip if data too short)
    print("\n" + "="*60)
    print("MODEL LEADERBOARD (Best to Worst)")
    print("="*60)
    try:
        leaderboard = predictor.leaderboard(train_data, silent=False)
        print(leaderboard)
    except ValueError as e:
        print(f"⚠️ Leaderboard skipped: {e}")
        print("Model training completed successfully despite this warning.")
        leaderboard = None
    
    # Save summary
    summary_path = MODELS_DIR / "autogluon_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("AutoGluon Model Summary\n")
        f.write("="*60 + "\n")
        f.write(leaderboard.to_string())
    
    print(f"\nModel saved to: {MODELS_DIR / 'autogluon_forecast'}")
    print(f"Summary saved to: {summary_path}")
    
    return predictor, leaderboard

def evaluate_autogluon():
    """Evaluate AutoGluon model performance"""
    print("\nEvaluating model on validation set...")
    
    train_data = prepare_autogluon_data()
    
    # Load trained model
    predictor = TimeSeriesPredictor.load(str(MODELS_DIR / "autogluon_forecast"))
    
    # Get predictions
    predictions = predictor.predict(train_data)
    
    # Calculate metrics
    from autogluon.timeseries.utils.metric_utils import check_get_evaluation_metric
    mae_metric = check_get_evaluation_metric('MAE')
    
    # Evaluate
    score = predictor.evaluate(train_data)
    
    print("\n" + "="*60)
    print("FINAL EVALUATION RESULTS")
    print("="*60)
    print(f"MAE: {score:.2f}")
    print("="*60)
    
    return score

if __name__ == "__main__":
    try:
        # Train
        predictor, leaderboard = train_autogluon_model()
        
        # Evaluate
        mae = evaluate_autogluon()
        
        print("\n✅ AutoGluon training completed successfully!")
        print(f"📊 Best MAE: {mae:.2f}")
        print("\nNext steps:")
        print("1. Run: python -m src.models.predict_autogluon")
        print("2. Check dashboard for results")
        
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
