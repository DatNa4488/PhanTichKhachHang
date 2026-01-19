@echo off
echo Running Data Pipeline...
.\.venv\Scripts\python -m src.data.ingest
.\.venv\Scripts\python -m src.data.clean
.\.venv\Scripts\python -m src.data.build_marts

echo Running Analytics & Forecasting...
.\.venv\Scripts\python -m src.features.rfm
.\.venv\Scripts\python -m src.models.train
.\.venv\Scripts\python -m src.models.evaluate
.\.venv\Scripts\python -m src.models.predict

echo Pipeline Complete!
pause
