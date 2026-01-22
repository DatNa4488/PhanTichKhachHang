# BÁO CÁO ĐỒ ÁN: HỆ THỐNG KHOA HỌC DỮ LIỆU BÁN LẺ

## 1. BÀI TOÁN & DỮ LIỆU (Problem & Data Understanding)

### 1.1. Bối Cảnh & Mục Tiêu
Doanh nghiệp bán lẻ đối mặt với bài toán tồn kho: nhập ít thì mất khách, nhập nhiều thì ứ đọng vốn.
**Mục tiêu đề tài**:
1.  **Phân tích hành vi (Customer Analytics)**: Hiểu khách hàng để marketing đúng người.
2.  **Dự báo nhu cầu (Forecasting)**: Dự đoán chính xác số lượng hàng bán tuần tới.

### 1.2. Dữ Liệu Online Retail
Dữ liệu giao dịch thực tế gồm: `InvoiceNo`, `StockCode`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`.

**Các vấn đề dữ liệu chính**:
-   **Đơn hủy**: `InvoiceNo` chứa ký tự 'C'.
-   **Thiếu định danh**: 25% dòng không có `CustomerID`.
-   **Nhiễu**: Số lượng âm, đơn giá bằng 0.

---

## 2. THIẾT KẾ HỆ THỐNG & TIỀN XỬ LÝ (System Design & Data Pipeline)

### 2.1. Kiến Trúc Hệ Thống
Mô hình đường ống dữ liệu (Pipeline):
`Raw Data` -> `Cleaning` -> `Feature Engineering` -> `Models` -> `Dashboard`.

### 2.2. Quy Trình Làm Sạch (Code Minh Họa)
*File: `src/data/clean.py`*

Quy tắc: Loại bỏ đơn hủy và dữ liệu thiếu ID để đảm bảo tính chính xác cho bài toán hành vi.

```python
# CODE THỰC TẾ:
# 1. Bỏ khách hàng thiếu ID
df = df.dropna(subset=['CustomerID']) 
# 2. Bỏ đơn hàng hủy (có chữ C ở đầu)
df = df[~df['InvoiceNo'].str.startswith('C')]
# 3. Lọc số lượng dương
df = df[df['Quantity'] > 0]
```

### 2.3. Các Bảng Dữ Liệu Đầu Ra
-   `sales_clean`: Dữ liệu sạch.
-   `demand_weekly`: Tổng hợp theo tuần (cho Forecast).
-   `customer_segments`: Kết quả phân nhóm (cho Marketing).

---

## 3. PHÂN TÍCH HÀNH VI KHÁCH HÀNG (Customer Behavior Analysis)

### 3.1. Phương Pháp RFM
Đánh giá khách hàng qua: **R**ecency (Mới mua), **F**requency (Mua nhiều lần), **M**onetary (Chi nhiều tiền).

### 3.2. Thuật Toán Phân Nhóm (Code Minh Họa)
*File: `src/features/rfm.py`*

Sử dụng thuật toán chia điểm **Quantile** (Tứ phân vị) để gán điểm 1-4.

```python
# CODE THỰC TẾ:
# Chia dữ liệu thành 4 phần bằng nhau, gán nhãn 1-4
df['R_Score'] = pd.qcut(df['Recency'], 4, labels=[4, 3, 2, 1]) # R thấp là tốt -> Đảo nhãn
df['F_Score'] = pd.qcut(df['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
df['M_Score'] = pd.qcut(df['Monetary'], 4, labels=[1, 2, 3, 4])

# Logic gán nhãn
def segment(row):
    if row['R_Score'] >= 4 and row['F_Score'] + row['M_Score'] >= 8:
        return 'Champions (VIP)'
    # ... các rủi ro khác
```

**Kết quả phân nhóm**:
-   **VIP**: Chăm sóc đặc biệt.
-   **Loyal**: Duy trì tương tác.
-   **At Risk**: Gửi mã giảm giá để giữ chân.

---

## 4. DỰ BÁO NHU CẦU SẢN PHẨM (Demand Forecasting)

### 4.1. Bài Toán & Đặc Trưng
Dự báo `Quantity` của **Tuần kế tiếp** cho từng `StockCode`.
**Feature Engineering** (*File: `src/features/timeseries_features.py`*):
-   **Lags**: Sức mua của 1, 2, 4 tuần trước.
-   **Rolling**: Trung bình 4 tuần gần nhất.

```python
# CODE THỰC TẾ:
# Tạo độ trễ (Lag)
df['lag_1'] = grouped['Quantity'].shift(1)
df['rolling_mean'] = grouped['Quantity'].rolling(window=4).mean()
```

### 4.2. Mô Hình Machine Learning
*File: `src/models/train.py`*

-   **Thuật toán**: **Random Forest Regressor** (Rừng ngẫu nhiên).
    -   *Tại sao chọn?*: Đây là thuật toán mạnh mẽ, có khả năng học được các tương tác phi tuyến tính phức tạp giữa các đặc trưng (ví dụ: mối quan hệ giữa "tháng" và "số lượng bán"). Nó cũng ít bị ảnh hưởng bởi nhiễu (outliers) và không yêu cầu dữ liệu phải tuân theo phân phối chuẩn như hồi quy tuyến tính.
-   **Huấn luyện**:
    ```python
    # Khởi tạo mô hình với 100 cây quyết định
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    ```
-   **Đánh giá Mô hình (Evaluation)**:
    -   **Time Series Cross-Validation**: Khác với kiểm thử thông thường (chia ngẫu nhiên), dữ liệu chuỗi thời gian buộc phải chia theo thứ tự thời gian.
        *   *Fold 1*: Train (Tuần 1-10) -> Test (Tuần 11).
        *   *Fold 2*: Train (Tuần 1-11) -> Test (Tuần 12).
        *   *Mục đích*: Đảm bảo mô hình không "nhìn trước tương lai" (data leakage).
    -   **MAE (Mean Absolute Error)**: Sai số tuyệt đối trung bình.
        *   *Ý nghĩa*: Trung bình mỗi dự báo bị lệch bao nhiêu sản phẩm so với thực tế. (Ví dụ: MAE = 5 nghĩa là dự báo sai lệch khoảng 5 cái). Chỉ số này càng thấp càng tốt.

---

## 5. TRIỂN KHAI & KẾT LUẬN (Implementation & Conclusion)

### 5.1. Ứng Dụng Streamlit
Hệ thống được đóng gói thành Web App giúp người dùng:
-   Xem báo cáo doanh thu.
-   Tra cứu danh sách khách hàng VIP.
-   Tải file dự báo nhập hàng.

### 5.2. Kết Luận
Dự án đã hoàn thành mục tiêu xây dựng một quy trình khoa học dữ liệu khép kín (End-to-End Data Science), giải quyết hai bài toán cốt lõi:
1.  **Hiểu khách hàng**: Đã phân loại thành công các nhóm khách hàng (VIP, Rời bỏ...) làm cơ sở cho các chiến dịch Marketing cá nhân hóa.
2.  **Tối ưu vận hành**: Đã xây dựng mô hình dự báo với độ chính xác chấp nhận được (tốt hơn trung bình), giúp hỗ trợ ra quyết định nhập hàng.
Hệ thống không chỉ dừng lại ở code mà đã được đóng gói thành ứng dụng trực quan, sẵn sàng để người dùng doanh nghiệp sử dụng.

### 5.3. Hướng Phát Triển & Mở Rộng
Để hệ thống hoàn thiện và ứng dụng thực tế sâu hơn, nhóm đề xuất các hướng cải tiến:
1.  **Làm Giàu Dữ Liệu (Data Enrichment)**:
    -   Tích hợp lịch sử **Khuyến Mãi/Giảm Giá**: Để mô hình học được tác động của việc giảm giá lên sức mua.
    -   Bổ sung yếu tố **Mùa Vụ & Lễ Tết**: Gắn cờ các ngày Black Friday, Giáng Sinh vào mô hình.
2.  **Nâng Cấp Mô Hình AI (Advanced Models)**:
    -   Thử nghiệm **Deep Learning (LSTM/Transformer)**: Cho các mã sản phẩm chủ lực (Top 50) có lịch sử dài, giúp bắt các quy luật phức tạp hơn.
    -   Tối ưu tham số tự động (Hyperparameter Tuning): Dùng GridSearch để tinh chỉnh Random Forest.
3.  **Triển Khai Mở Rộng (Deployment)**:
    -   Đóng gói Docker Container để dễ dàng cài đặt trên server.
    -   Lập lịch chạy tự động (Schedule) hàng tuần bằng Airflow/Cronjob để tự động cập nhật dự báo mới.

---

## 6. PHÂN CÔNG NHÓM (5 Thành Viên)

| Thành Viên | Vai Trò | Nhiệm Vụ Cụ Thể (Gắn với Code) | Output |
| :--- | :--- | :--- | :--- |
| **Bạn A** | **Data Engineer** | Viết luật làm sạch (`clean.py`), tạo bảng Marts. | `src/data/` |
| **Bạn B** | **Data Analyst** | Phân tích EDA, tìm Outlier, vẽ biểu đồ. | `notebooks/01_eda.ipynb` |
| **Bạn C** | **Customer Analyst** | Cài đặt thuật toán RFM, định nghĩa luật phân khúc. | `src/features/rfm.py` |
| **Bạn D** | **AI Engineer** | Tạo Feature Lags, huấn luyện Random Forest. | `src/models/train.py` |
| **Bạn E** | **Fullstack App** | Xây dựng Dashboard Streamlit, tích hợp và viết báo cáo. | `src/app/`, `reports/` |
