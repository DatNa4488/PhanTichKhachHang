import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Data Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Reports Directories
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
FORECAST_OUTPUTS_DIR = REPORTS_DIR / "forecast_outputs"

# Models Directory
MODELS_DIR = PROJECT_ROOT / "models"

# File Paths
RAW_DATA_FILE = RAW_DATA_DIR / "Online Retail.xlsx"
CLEAN_SALES_FILE = PROCESSED_DATA_DIR / "sales_clean.parquet"
CUSTOMER_TRANSACTIONS_FILE = PROCESSED_DATA_DIR / "customer_transactions.parquet"
WEEKLY_DEMAND_FILE = PROCESSED_DATA_DIR / "demand_weekly.parquet"
CUSTOMER_SEGMENTS_FILE = PROCESSED_DATA_DIR / "customer_segments.parquet"

# Configs
RANDOM_STATE = 42
DATE_FORMAT = "%Y-%m-%d"
