# GIẢI THÍCH CHI TIẾT LOGIC PHÂN KHÚC KHÁCH HÀNG (RFM)

Tài liệu này giải thích cặn kẽ đoạn code phân khúc khách hàng để bạn hiểu rõ bản chất khi bảo vệ đồ án.

---

## 1. Bản Chất Của "Chia Điểm" (Scoring)
Trong đoạn code:
```python
df['R_Score'] = pd.qcut(df['Recency'], 4, labels=[4, 3, 2, 1])
```

### `pd.qcut` là gì?
Hàm này chia dữ liệu thành **4 phần bằng nhau** (gọi là 4 Quartiles - Tứ phân vị).
-   Tưởng tượng lớp có 100 học sinh. `qcut` sẽ xếp hàng từ điểm thấp đến cao và cắt thành 4 nhóm, mỗi nhóm 25 bạn.
-   **Nhóm 1**: 25% thấp nhất.
-   **Nhóm 2**: 25% trung bình thấp.
-   **Nhóm 3**: 25% trung bình cao.
-   **Nhóm 4**: 25% cao nhất.

### Tại sao `Recency` lại gán nhãn ngược `[4, 3, 2, 1]`?
-   **Recency (R)**: Số ngày kể từ lần mua cuối.
    -   Ví dụ: Mới mua hôm qua (R=1) là **TỐT**.
    -   Mua từ năm ngoái (R=365) là **XẤU**.
    -   => Giá trị R càng **NHỎ** thì điểm phải càng **CAO**.
    -   Nên ta gán nhãn ngược: Nhóm giá trị nhỏ nhất nhận điểm 4, nhóm lớn nhất nhận điểm 1.

-   **Frequency (F) & Monetary (M)**:
    -   Mua càng nhiều (F cao) -> Tốt -> Điểm cao.
    -   Chi càng nhiều (M cao) -> Tốt -> Điểm cao.
    -   => Gán nhãn xuôi `[1, 2, 3, 4]`.

---

## 2. Ví Dụ Minh Họa Bằng Số Liệu Cụ Thể

Giả sử ta tính được chỉ số phân vị (ngưỡng cắt) từ dữ liệu toàn bộ khách hàng như sau:

| Điểm số (Score) | Recency (Ngày) | Frequency (Lần) | Monetary ($) |
| :--- | :--- | :--- | :--- |
| **Điểm 1 (Tệ nhất)** | > 200 ngày | 1 lần | < 100$ |
| **Điểm 2** | 100 - 200 ngày | 2 - 3 lần | 100$ - 300$ |
| **Điểm 3** | 30 - 100 ngày | 4 - 8 lần | 300$ - 1000$ |
| **Điểm 4 (Tốt nhất)**| < 30 ngày | > 8 lần | > 1000$ |

### Xét 2 khách hàng thực tế:

#### Khách hàng A (Ông Vua Mua Sắm)
-   **Dữ liệu thực**: Mới mua hôm qua (R=1), Mua 20 lần (F=20), Chi 5000$ (M=5000).
-   **Tính điểm**:
    -   R=1 nằm trong nhóm "Tốt nhất" (<30) -> **R_Score = 4**.
    -   F=20 nằm trong nhóm "Tốt nhất" (>8) -> **F_Score = 4**.
    -   M=5000 nằm trong nhóm "Tốt nhất" (>1000) -> **M_Score = 4**.
-   **Kết quả**: Điểm 444.

#### Khách hàng B (Khách Đã Bỏ Đi)
-   **Dữ liệu thực**: Mua cách đây 1 năm (R=365), Mua 1 lần (F=1), Chi 50$ (M=50).
-   **Tính điểm**:
    -   R=365 nằm trong nhóm "Tệ nhất" (>200) -> **R_Score = 1**.
    -   F=1 nằm trong nhóm "Tệ nhất" (1) -> **F_Score = 1**.
    -   M=50 nằm trong nhóm "Tệ nhất" (<100) -> **M_Score = 1**.
-   **Kết quả**: Điểm 111.

---

## 3. Giải Thích Logic Gán Nhãn ("Segment")

Đoạn code trong hàm `segment(row)` hoạt động như sau:

```python
# Điểm trung bình của Tần suất và Tiền (FM Average)
# Vì thường Frequency và Monetary đi đôi với nhau (mua nhiều thì tốn nhiều tiền)
# Nên ta gộp chung lại cho đơn giản hóa logic.
fm = (f + m) / 2
```

### Các tập luật (Rules):

1.  **Champions (Nhà Vô Địch - Khách VIP)**
    -   `if r >= 4 and fm >= 4`:
    -   **Nghĩa là**: Vừa mới mua gần đây (R=4) **VÀ** Chi tiêu/Mua sắm rất khủng (FM=4).
    -   *Hành động*: Tặng quà tri ân, ưu tiên chăm sóc 1-1.

2.  **Loyal Customers (Khách Trung Thành)**
    -   `elif r >= 3 and fm >= 3`:
    -   **Nghĩa là**: Mua khá gần đây (R=3) **VÀ** Chi tiêu ở mức Khá (FM=3).
    -   *Hành động*: Giới thiệu sản phẩm mới, upsell.

3.  **Hibernating (Ngủ Đông)**
    -   `elif r <= 2 and fm <= 2`:
    -   **Nghĩa là**: Đã lâu không quay lại (R thấp) **VÀ** Trước đó cũng mua ít/chi ít (FM thấp).
    -   *Hành động*: Tiết kiệm ngân sách, thỉnh thoảng gửi email nhắc nhở, không cần dồn lực.

4.  **At Risk (Nguy Cơ Rời Bỏ - Cần chú ý!)**
    -   `elif r <= 2 and fm >= 3`: (Logic bổ sung thường gặp)
    -   **Nghĩa là**: Đã lâu không quay lại (R thấp) **NHƯNG** Trong quá khứ từng mua rất nhiều (FM cao).
    -   *Hành động*: **RẤT QUAN TRỌNG**. Đây là khách VIP đang chán mình. Phải gọi điện, tặng voucher khủng để kéo họ về ngay.

---

## Tóm Lại
Bạn chỉ cần nhớ quy tắc "Thần Chú" này khi thuyết trình:
> "**R** càng nhỏ điểm càng cao. **F** và **M** càng to điểm càng cao. Chúng em dùng thuật toán chia nhóm (Quantile) để máy tự động chấm điểm khách hàng từ 1 đến 4, sau đó dùng luật kinh doanh để gọi tên nhóm khách hàng đó."
