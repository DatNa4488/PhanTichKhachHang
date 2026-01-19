# Retail Demand Forecasting & Customer Behavior Analysis

Dự án này là một hệ thống khoa học dữ liệu đầu cuối (end-to-end) nhằm phân tích hành vi mua hàng của khách hàng và dự báo nhu cầu sản phẩm.

## Cấu Trúc Dự Án

```
retail-demand-forecast/
│
├── data/               # Dữ liệu (raw và processed)
├── notebooks/          # Jupyter notebooks cho phân tích và thử nghiệm
├── src/                # Mã nguồn chính
│   ├── data/           # Script xử lý dữ liệu
│   ├── features/       # Script tạo đặc trưng (feature engineering)
│   ├── models/         # Script huấn luyện và dự báo
│   └── app/            # Ứng dụng Streamlit
├── reports/            # Báo cáo và kết quả đầu ra
├── tests/              # Kiểm thử
├── requirements.txt    # Các thư viện phụ thuộc
└── README.md           # Hướng dẫn dự án
```

## Cài Đặt

1.  **Clone hoặc tạo dự án**: Đảm bảo bạn đang ở thư mục gốc `retail-demand-forecast`.
2.  **Tạo môi trường ảo** (khuyên dùng):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```

## Hướng Dẫn Chạy

### 1. Đường Ống Dữ Liệu (Data Pipeline)
Thực hiện lần lượt các bước sau để xử lý dữ liệu từ file Excel gốc:

```bash
# Nhập dữ liệu và kiểm tra sơ bộ
python -m src.data.ingest

# Làm sạch dữ liệu
python -m src.data.clean

# Tạo các bảng phân tích (Data Marts)
python -m src.data.build_marts
```

### 2. Phân Tích & Dự Báo
```bash
# Phân khúc khách hàng (RFM)
python -m src.features.rfm

# Huấn luyện mô hình và dự báo
python -m src.models.train
python -m src.models.predict
```

### 3. Chạy Ứng Dụng (Dashboard)
```bash
streamlit run src/app/streamlit_app.py
```

## Ghi Chú
- Dữ liệu gốc `Online Retail.xlsx` cần được đặt trong thư mục gốc của dự án.
- Các kết quả dự báo sẽ được lưu trong `reports/forecast_outputs`.
