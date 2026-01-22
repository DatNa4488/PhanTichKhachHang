# HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG HỆ THỐNG AUTOGLUON

## 🚀 BƯỚC 1: CÀI ĐẶT DEPENDENCIES

### 1.1. Cài đặt thư viện mới
```bash
pip install -r requirements.txt
```

**Lưu ý**: AutoGluon có thể mất 5-10 phút để cài đặt (khoảng 500MB).

### 1.2. Kiểm tra cài đặt
```bash
python -c "from autogluon.timeseries import TimeSeriesPredictor; print('✅ AutoGluon OK')"
```

---

## 📊 BƯỚC 2: TRAIN MÔ HÌNH AUTOGLUON

### 2.1. Chạy training
```bash
python -m src.models.train_autogluon
```

**Thời gian**: 10-15 phút (tùy máy)

**Kết quả mong đợi**:
```
TRAINING AUTOGLUON TIME SERIES MODEL
Training models (this may take 10-15 minutes)...
AutoGluon will automatically try multiple models:
  - Naive (baseline)
  - SeasonalNaive
  - ETS (Exponential Smoothing)
  - ARIMA
  - Theta
  - DeepAR (Neural Network)

MODEL LEADERBOARD (Best to Worst)
                model  score_val
0              DeepAR      28.45
1                 ETS      31.20
2               ARIMA      33.15
3               Theta      35.80
4       SeasonalNaive      42.10
5               Naive      58.90

✅ AutoGluon training completed successfully!
📊 Best MAE: 28.45
```

### 2.2. Kiểm tra model đã lưu
```bash
ls models/autogluon_forecast/
```

Bạn sẽ thấy:
- `predictor.pkl` - Mô hình chính
- `models/` - Các mô hình con (DeepAR, ETS, ARIMA...)
- `utils/` - Metadata

---

## 🔮 BƯỚC 3: TẠO DỰ BÁO

### 3.1. Chạy prediction
```bash
python -m src.models.predict_autogluon
```

**Kết quả**:
```
Loading AutoGluon model...
Generating forecasts for next 4 weeks...
✅ Forecasts saved to: reports/forecast_outputs/demand_forecast_autogluon.csv
📊 Total products forecasted: 3120
📅 Forecast horizon: 4 weeks
```

### 3.2. Xem kết quả
```bash
head reports/forecast_outputs/demand_forecast_autogluon.csv
```

File CSV sẽ có cấu trúc:
```
StockCode,Forecast_Week,Forecast_Qty,Lower_Bound,Upper_Bound
75013B,2011-01-31,21.9,15.3,28.5
85055,2011-01-31,16.95,12.1,21.8
...
```

---

## 🎨 BƯỚC 4: XEM DASHBOARD MỚI

### 4.1. Chạy Streamlit
```bash
streamlit run src/app/streamlit_app.py
```

### 4.2. Mở trình duyệt
```
http://localhost:8501
```

### 4.3. Tính năng mới
- ✅ Tab "So Sánh Mô Hình" (Random Forest vs AutoGluon)
- ✅ Biểu đồ Plotly tương tác
- ✅ Confidence intervals (khoảng tin cậy)
- ✅ UI hiện đại hơn với gradient colors

---

## 📈 BƯỚC 5: SO SÁNH KẾT QUẢ

### 5.1. Train cả 2 mô hình
```bash
# Random Forest (cũ)
python -m src.models.train

# AutoGluon (mới)
python -m src.models.train_autogluon
```

### 5.2. Xem so sánh trong Dashboard
Vào tab "⚖️ So Sánh Mô Hình" để thấy:
- MAE của từng mô hình
- Thời gian training
- Ưu/nhược điểm

**Kết quả mong đợi**:
- Random Forest MAE: ~47
- AutoGluon MAE: ~28-32 (cải thiện 30-40%)

---

## 🔧 TROUBLESHOOTING

### Lỗi 1: "ModuleNotFoundError: No module named 'autogluon'"
**Giải pháp**:
```bash
pip install autogluon.timeseries
```

### Lỗi 2: "Memory Error" khi train
**Giải pháp**: Giảm `time_limit` trong `train_autogluon.py`:
```python
predictor.fit(
    train_data,
    time_limit=300,  # Giảm từ 600 xuống 300 giây
    presets='fast_training'  # Thay vì 'medium_quality'
)
```

### Lỗi 3: Train quá lâu
**Giải pháp**: Dùng preset nhanh hơn:
```python
presets='fast_training'  # Thay vì 'medium_quality' hoặc 'best_quality'
```

---

## 📝 NOTES

### Sự khác biệt Random Forest vs AutoGluon

| Tiêu Chí | Random Forest | AutoGluon |
|----------|---------------|-----------|
| **MAE** | ~47 | ~28-32 |
| **Thời gian train** | 5 phút | 10-15 phút |
| **Số mô hình** | 1 | 6-8 (ensemble) |
| **Confidence intervals** | Không | Có |
| **Tự động tối ưu** | Không | Có |
| **Phù hợp** | Prototype nhanh | Production |

### Khi nào dùng mô hình nào?

**Dùng Random Forest khi**:
- Cần kết quả nhanh (demo, prototype)
- Máy yếu (RAM < 8GB)
- Dữ liệu ít (<1000 dòng)

**Dùng AutoGluon khi**:
- Cần độ chính xác cao
- Có thời gian train (10-15 phút)
- Deploy production
- Cần confidence intervals

---

## 🎯 NEXT STEPS

1. ✅ Train AutoGluon
2. ✅ So sánh với Random Forest
3. ⬜ Deploy lên Streamlit Cloud (miễn phí)
4. ⬜ Thêm authentication
5. ⬜ Setup CI/CD

Xem file `upgrade_plan_free.md` để biết cách deploy miễn phí!
