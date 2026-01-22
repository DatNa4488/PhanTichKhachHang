# BÁO CÁO PHÂN TÍCH DỰ ÁN: HỆ THỐNG KHOA HỌC DỮ LIỆU BÁN LẺ

## 1. Mục Tiêu Đề Tài
Xây dựng một hệ thống khoa học dữ liệu khép kín (End-to-End Data Science System) nhằm giải quyết hai bài toán cốt lõi của doanh nghiệp bán lẻ:
1.  **Hiểu khách hàng (Customer Understanding)**: Phân khúc khách hàng dựa trên hành vi mua sắm để tối ưu hóa chiến lược marketing và chăm sóc khách hàng.
2.  **Tối ưu nguồn hàng (Inventory Optimization)**: Dự báo nhu cầu tiêu thụ hàng hóa trong tương lai để hỗ trợ ra quyết định nhập hàng, giảm tồn kho.

---

## 2. Cấu Trúc Hệ Thống (System Architecture)
Hệ thống được thiết kế theo mô hình đường ống dữ liệu (Data Pipeline) chuẩn mực, đi từ dữ liệu thô đến ứng dụng cuối cùng.

### Luồng Dữ Liệu (Data Flow):
1.  **Raw Data**: Dữ liệu giao dịch gốc (`online_retail_raw.parquet`).
2.  **Preprocessing (ETL)**: Làm sạch và chuẩn hóa dữ liệu (`src/data`).
3.  **Feature Store**: Kho chứa các đặc trưng đã tính toán (`sales_clean.parquet`, `customer_segments.parquet`).
4.  **Modeling**: Huấn luyện các mô hình AI/ML (`src/models`, `src/features`).
5.  **Application**: Giao diện người dùng để tương tác (`src/app/streamlit_app.py`).

---

## 3. Quy Trình Xử Lý Dữ Liệu (Data Processing)
Dữ liệu được xử lý qua các bước nghiêm ngặt để đảm bảo chất lượng đầu vào cho mô hình.

### 3.1. Làm sạch dữ liệu (Data Cleaning)
*File code minh họa: `src/data/clean.py`*

Quá trình làm sạch bao gồm các bước chính:
-   **Loại bỏ dữ liệu thiếu**: Xóa các dòng không có `CustomerID` vì không thể phân tích hành vi nặc danh.
-   **Xử lý đơn hủy**: Loại bỏ các đơn hàng có `InvoiceNo` bắt đầu bằng ký tự 'C' (Cancellation) để tính toán nhu cầu thực tế chính xác hơn.
-   **Lọc nhiễu**: Loại bỏ các dòng có số lượng (`Quantity`) hoặc đơn giá (`UnitPrice`) nhỏ hơn hoặc bằng 0.

```python
# Trích đoạn code xử lý (src/data/clean.py)
df = df.dropna(subset=['CustomerID'])  # Bỏ khách hàng thiếu ID
df = df[~df['InvoiceNo'].str.startswith('C')]  # Bỏ đơn hủy
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]  # Chỉ lấy số dương
```

### 3.2. Kỹ thuật đặc trưng (Feature Engineering)
*File code minh họa: `src/features/timeseries_features.py`*

Để mô hình dự báo hiểu được tính chu kỳ và xu hướng, chúng ta tạo ra các đặc trưng thời gian:
-   **Lag Features (Biến trễ)**: Nhu cầu của 1 tuần, 2 tuần, 4 tuần trước.
-   **Rolling Window Features (Cửa sổ trượt)**: Trung bình cộng số lượng bán trong 4 tuần gần nhất.
-   **Time Features**: Tháng trong năm, Tuần trong năm.

---

## 4. Thuật Toán & Đánh Giá Mô Hình (Algorithms & Evaluation)

### 4.1. Phân Khúc Khách Hàng (Customer Segmentation)
*File code: `src/features/rfm.py`*

Sử dụng mô hình **RFM (Recency - Frequency - Monetary)**. Đây là phương pháp kinh điển trong Marketing nhưng được triển khai bằng thuật toán chia nhóm thống kê (**Quantile/Ranking**).

-   **Recency (R)**: Số ngày từ lần mua cuối cùng.
-   **Frequency (F)**: Tần suất mua hàng.
-   **Monetary (M)**: Tổng số tiền đã chi tiêu.

**Thuật toán thực hiện:**
1.  Tính giá trị R, F, M cho từng khách hàng.
2.  Dùng hàm `pd.qcut` để chia dữ liệu thành 4 phần bằng nhau (quartiles), gán điểm từ 1 đến 4.
3.  Kết hợp điểm để phân loại khách hàng (Ví dụ: R=4, F=4, M=4 là khách hàng VIP).

```python
# Trích đoạn code phân khúc (src/features/rfm.py)
df['R_Score'] = pd.qcut(df['Recency'], 4, labels=[4, 3, 2, 1])
df['F_Score'] = pd.qcut(df['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
df['M_Score'] = pd.qcut(df['Monetary'], 4, labels=[1, 2, 3, 4])
```

### 4.2. Dự Báo Nhu Cầu (Demand Forecasting)
*File code: `src/models/train.py`*

Sử dụng thuật toán học máy **Random Forest Regressor** (Rừng ngẫu nhiên).
-   **Lý do chọn**: Random Forest xử lý tốt dữ liệu bảng (tabular data), không cần chuẩn hóa khắt khe (scaling), và có khả năng nắm bắt các tương tác phi tuyến tính giữa các biến.

**Đánh giá mô hình (Model Evaluation):**
-   Sử dụng phương pháp **Time Series Cross-Validation**: Không chia ngẫu nhiên (k-fold) mà chia theo trục thời gian (Quá khứ train -> Tương lai test) để tránh lỗi "nhìn trước tương lai" (data leakage).
-   Độ đo sai số: **MAE (Mean Absolute Error)** - Sai lệch tuyệt đối trung bình, dễ hiểu về mặt kinh doanh (sai lệch bao nhiêu sản phẩm).

```python
# Trích đoạn code huấn luyện (src/models/train.py)
tscv = TimeSeriesSplit(n_splits=3) # Chia tập test theo thời gian
model = RandomForestRegressor(n_estimators=100) # Mô hình Rừng ngẫu nhiên
mae = mean_absolute_error(y_test, preds) # Đánh giá sai số
```

---

## 5. Đầu Vào & Đầu Ra Chi Tiết (Inputs / Outputs)

| Loại | Chi Tiết | File/Thư mục |
| :--- | :--- | :--- |
| **Đầu Vào (Input)** | Dữ liệu giao dịch thô: `InvoiceNo`, `StockCode`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`. | `data/raw/online_retail_raw.parquet` |
| **Đầu Ra (Output) 1** | Bảng phân khúc khách hàng: Mỗi CustomerID gắn với nhãn (VIP, At Risk, Loyal...). | `data/processed/customer_segments.parquet` |
| **Đầu Ra (Output) 2** | Bảng dự báo nhu cầu: Số lượng dự kiến bán của từng sản phẩm trong tuần tới. | `models/rf_forecast_model.pkl` & CSV kết quả |
| **Giao Diện** | Dashboard tương tác hiển thị biểu đồ và bảng số liệu. | `http://localhost:8501` |

---

## 6. Phân Công Nhiệm Vụ Nhóm (5 Thành Viên)
*Dựa trên cấu trúc dự án thực tế và khối lượng công việc.*

### **Bạn A — Data/SQL & Cleaning**
*Chịu trách nhiệm về chất lượng dữ liệu đầu vào.*
-   **Nhiệm vụ**:
    -   Xây dựng bộ quy tắc làm sạch dữ liệu (loại bỏ âm, xử lý missing).
    -   Tạo pipeline chuyển đổi dữ liệu thô sang dữ liệu sạch (`sales_clean`).
    -   Chuẩn bị bảng dữ liệu tổng hợp theo tuần (`demand_weekly`) cho mô hình.
-   **Sản phẩm (Output)**:
    -   `src/data/clean.py` (Script làm sạch chính).
    -   `src/data/build_marts.py` (Script tổng hợp dữ liệu).
    -   File `data/processed/sales_clean.parquet`.

### **Bạn B — EDA & Insight Analyst**
*Chịu trách nhiệm thấu hiểu dữ liệu và tìm ra insight.*
-   **Nhiệm vụ**:
    -   Phân tích khám phá dữ liệu (EDA).
    -   Vẽ biểu đồ xu hướng doanh thu, top sản phẩm bán chạy.
    -   Phát hiện các điểm bất thường (outlier) trong dữ liệu.
-   **Sản phẩm (Output)**:
    -   `notebooks/01_eda.ipynb` (Notebook chứa biểu đồ và nhận xét).
    -   Các hình ảnh biểu đồ trong báo cáo.

### **Bạn C — Customer Analytics (RFM)**
*Chuyên sâu về phân tích khách hàng.*
-   **Nhiệm vụ**:
    -   Nghiên cứu và cài đặt thuật toán RFM.
    -   Tính toán điểm số R-F-M cho từng khách hàng.
    -   Định nghĩa luật phân nhóm (Ví dụ: Ai là VIP? Ai sắp rời bỏ?).
-   **Sản phẩm (Output)**:
    -   `src/features/rfm.py` (Code thuật toán RFM).
    -   `notebooks/02_rfm_analysis.ipynb` (Phân tích sâu về các nhóm khách).

### **Bạn D — Forecast Modeling (Dự báo)**
*Chịu trách nhiệm xây dựng bộ não AI cho hệ thống.*
-   **Nhiệm vụ**:
    -   Xây dựng mô hình Baseline và Random Forest.
    -   Viết code huấn luyện (`train`) và đánh giá (`evaluate`) kiểm thử chéo.
    -   Tạo script dự báo cho dữ liệu mới (`predict`).
-   **Sản phẩm (Output)**:
    -   `src/models/train.py`, `src/models/evaluate.py`, `src/models/predict.py`.
    -   File model: `models/rf_forecast_model.pkl`.

### **Bạn E — App Development & Reporting**
*Kết nối tất cả thành sản phẩm cuối cùng.*
-   **Nhiệm vụ**:
    -   Xây dựng giao diện Dashboard bằng Streamlit.
    -   Tích hợp code của các bạn A, B, C, D vào ứng dụng.
    -   Viết tài liệu hướng dẫn (`README`) và kiểm thử cơ bản (`tests`).
-   **Sản phẩm (Output)**:
    -   `src/app/streamlit_app.py` (Giao diện người dùng).
    -   `README.md` (Tài liệu dự án).
    -   Thư mục `tests/`.
