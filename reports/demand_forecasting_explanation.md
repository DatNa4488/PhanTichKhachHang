# GIẢI THÍCH CHI TIẾT: DỰ BÁO NHU CẦU HÀNG HÓA

Tài liệu này phân tích rõ ràng bài toán dự báo nhu cầu, cách thức hoạt động và tác dụng thực tế của nó trong kinh doanh.

---

## 1. BÀI TOÁN DỰ BÁO NHU CẦU LÀ GÌ?

### Định Nghĩa
**Dự báo nhu cầu (Demand Forecasting)** là việc dự đoán số lượng sản phẩm sẽ được bán ra trong một khoảng thời gian cụ thể ở tương lai.

### Ví Dụ Cụ Thể
Giả sử bạn bán áo phông:
-   **Tuần này** (Tuần 24/2011): Bán được **21.9 cái** (dữ liệu thực tế).
-   **Câu hỏi**: Tuần sau (Tuần 31/2011) sẽ bán được bao nhiêu cái?
-   **Mô hình dự báo**: Dựa vào lịch sử bán hàng, mô hình dự đoán tuần sau sẽ bán được **16.95 cái**.

Như trong ảnh bạn cung cấp:
-   Mã sản phẩm `85085` tuần `2011-01-31` dự báo bán được **16.95** cái.
-   Mã sản phẩm `470118` tuần `2011-01-31` dự báo bán được **17.07** cái.

---

## 2. TẠI SAO CẦN DỰ BÁO NHU CẦU?

### Vấn Đề Thực Tế Của Doanh Nghiệp

#### Tình Huống 1: Nhập Hàng Quá Ít
-   **Hậu quả**: Hết hàng khi khách đến mua → Khách chuyển sang mua của đối thủ → **Mất doanh thu**.
-   **Ví dụ**: Tuần sau thực tế bán được 100 cái nhưng chỉ nhập 50 cái → Thiệt hại 50 đơn hàng.

#### Tình Huống 2: Nhập Hàng Quá Nhiều
-   **Hậu quả**: Hàng tồn kho → Chiếm vốn, tốn chi phí lưu kho, hàng lỗi thời → **Lãng phí**.
-   **Ví dụ**: Dự đoán bán 100 cái nên nhập 100, nhưng thực tế chỉ bán được 30 → Tồn 70 cái.

### Giải Pháp: Dự Báo Chính Xác
Nếu có mô hình dự báo tốt:
-   Dự đoán tuần sau bán **80 cái** → Nhập đúng 80 cái.
-   **Kết quả**: Không thiếu hàng, không thừa hàng → **Tối ưu lợi nhuận**.

---

## 3. MÔ HÌNH DỰ BÁO HOẠT ĐỘNG NHƯ THẾ NÀO?

### Bước 1: Thu Thập Dữ Liệu Lịch Sử
Mô hình cần biết **quá khứ** để dự đoán **tương lai**.

**Ví dụ dữ liệu đầu vào** (Sản phẩm mã `85085`):
| Tuần | Số Lượng Bán (Thực Tế) |
| :--- | :--- |
| Tuần 1 | 15 cái |
| Tuần 2 | 18 cái |
| Tuần 3 | 22 cái |
| Tuần 4 | 20 cái |
| Tuần 5 | **?** (Cần dự báo) |

### Bước 2: Tạo Đặc Trưng (Feature Engineering)
Mô hình không chỉ nhìn vào "tuần trước bán bao nhiêu" mà còn học nhiều thông tin hơn:

#### a) Lag Features (Biến Độ Trễ)
-   `lag_1`: Số lượng bán của **tuần trước** (Tuần 4 = 20).
-   `lag_2`: Số lượng bán của **2 tuần trước** (Tuần 3 = 22).
-   `lag_4`: Số lượng bán của **4 tuần trước** (Tuần 1 = 15).

**Code thực tế**:
```python
df['lag_1'] = grouped['Quantity'].shift(1)  # Lấy giá trị tuần trước
df['lag_2'] = grouped['Quantity'].shift(2)  # Lấy giá trị 2 tuần trước
```

#### b) Rolling Mean (Trung Bình Trượt)
-   Tính trung bình số lượng bán trong **4 tuần gần nhất** để làm mượt xu hướng.
-   Ví dụ: `rolling_mean_4 = (15 + 18 + 22 + 20) / 4 = 18.75`.

**Code thực tế**:
```python
df['rolling_mean_4'] = grouped['Quantity'].rolling(window=4).mean()
```

#### c) Time Features (Đặc Trưng Thời Gian)
-   `Month`: Tháng trong năm (Tháng 12 thường bán nhiều hơn vì Giáng Sinh).
-   `WeekOfYear`: Tuần thứ mấy trong năm.

### Bước 3: Huấn Luyện Mô Hình Random Forest
Mô hình học mối quan hệ giữa các đặc trưng và kết quả:
-   **Input (X)**: `lag_1=20, lag_2=22, rolling_mean=18.75, Month=1, Week=5`.
-   **Output (Y)**: `Quantity = 19` (Dự báo).

**Code thực tế**:
```python
features = ['lag_1', 'lag_2', 'lag_4', 'rolling_mean_4', 'Month', 'WeekOfYear']
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)  # Học từ dữ liệu quá khứ
```

### Bước 4: Dự Báo Cho Tuần Mới
Khi cần dự báo tuần 5:
1.  Lấy dữ liệu tuần 1-4 làm đặc trưng.
2.  Đưa vào mô hình đã huấn luyện.
3.  Mô hình trả về: **Tuần 5 dự kiến bán 19 cái**.

---

## 4. TÁC DỤNG THỰC TẾ CỦA DỰ BÁO NHU CẦU

### 4.1. Tối Ưu Hóa Kho Hàng (Inventory Management)
-   **Trước khi có dự báo**: Nhập hàng theo cảm tính hoặc kinh nghiệm → Sai số cao.
-   **Sau khi có dự báo**: Nhập đúng số lượng cần thiết → Giảm tồn kho 20-30%.

**Ví dụ**:
-   Dự báo tuần sau bán 100 cái → Nhập 110 cái (dự phòng 10%).
-   Thực tế bán được 105 cái → Chỉ thừa 5 cái thay vì 50 cái như trước.

### 4.2. Lập Kế Hoạch Sản Xuất (Production Planning)
Nếu bạn tự sản xuất hàng:
-   Biết trước nhu cầu → Sắp xếp ca làm việc, đặt nguyên liệu đúng lúc.
-   **Tiết kiệm**: Chi phí gia công, chi phí lưu kho nguyên liệu.

### 4.3. Tối Ưu Chiến Dịch Marketing
-   Nếu dự báo tuần sau bán ít → Tung khuyến mãi để kích cầu.
-   Nếu dự báo tuần sau bán nhiều → Không cần giảm giá, tối đa hóa lợi nhuận.

### 4.4. Cải Thiện Trải Nghiệm Khách Hàng
-   Luôn có hàng khi khách cần → Khách hài lòng → Tăng lòng trung thành.

---

## 5. ĐÁNH GIÁ ĐỘ CHÍNH XÁC CỦA MÔ HÌNH

### Độ Đo MAE (Mean Absolute Error)
**Công thức**:
```
MAE = Trung bình của |Dự báo - Thực tế|
```

**Ví dụ**:
| Tuần | Dự Báo | Thực Tế | Sai Số |
| :--- | :--- | :--- | :--- |
| Tuần 5 | 19 | 21 | 2 |
| Tuần 6 | 25 | 23 | 2 |
| Tuần 7 | 18 | 20 | 2 |

MAE = (2 + 2 + 2) / 3 = **2 cái**.

**Ý nghĩa**: Trung bình mỗi lần dự báo sai lệch 2 cái so với thực tế.
-   MAE càng thấp → Mô hình càng chính xác.
-   MAE = 0 → Dự báo hoàn hảo (không thể xảy ra trong thực tế).

### Time Series Cross-Validation
Để đảm bảo mô hình không "gian lận" (nhìn trước tương lai), ta chia dữ liệu theo thời gian:
-   **Fold 1**: Train (Tuần 1-10) → Test (Tuần 11).
-   **Fold 2**: Train (Tuần 1-11) → Test (Tuần 12).
-   **Fold 3**: Train (Tuần 1-12) → Test (Tuần 13).

Mô hình chỉ được học từ **quá khứ** để dự đoán **tương lai**, giống như thực tế.

---

## 6. KẾT QUẢ THỰC TẾ TRONG DỰ ÁN

Như trong ảnh bạn cung cấp, hệ thống đã tạo ra file CSV chứa dự báo:
-   **Cột `StockCode`**: Mã sản phẩm cần dự báo.
-   **Cột `Forecast_Week`**: Tuần cần dự báo (ví dụ: `2011-01-24`).
-   **Cột `Forecast_Qty`**: Số lượng dự kiến bán (ví dụ: `21.9` cái).

**Cách sử dụng**:
1.  Người quản lý kho mở file CSV.
2.  Xem dự báo cho từng sản phẩm.
3.  Quyết định nhập hàng dựa trên con số dự báo.

---

## TÓM TẮT

| Khía Cạnh | Nội Dung |
| :--- | :--- |
| **Bài toán** | Dự đoán số lượng sản phẩm bán ra trong tương lai |
| **Đầu vào** | Lịch sử bán hàng (Quantity theo tuần) |
| **Đầu ra** | Số lượng dự kiến bán tuần/tháng tới |
| **Thuật toán** | Random Forest Regressor |
| **Đặc trưng chính** | Lag (độ trễ), Rolling Mean (trung bình trượt), Time (thời gian) |
| **Đánh giá** | MAE (sai số trung bình), Time Series CV |
| **Tác dụng** | Tối ưu kho, giảm tồn, tăng lợi nhuận, cải thiện trải nghiệm khách |
