import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

try:
    from src.config import CLEAN_SALES_FILE, CUSTOMER_SEGMENTS_FILE, FORECAST_OUTPUTS_DIR
except ImportError as e:
    st.error(f"Import Error: {e}. Please run the app from the project root using `streamlit run src/app/streamlit_app.py`")
    st.stop()

st.set_page_config(page_title="Dự Báo Nhu Cầu Bán Lẻ", layout="wide")

st.title("📊 Hệ Thống Khoa Học Dữ Liệu Bán Lẻ")
st.markdown("### Dự Báo Nhu Cầu & Phân Tích Khách Hàng")

# @st.cache_data
def load_data():
    try:
        sales = pd.read_parquet(CLEAN_SALES_FILE)
        cols = ['InvoiceDate', 'StockCode', 'Description', 'Quantity', 'UnitPrice', 'TotalValue', 'Country', 'CustomerID']
        # Load segments if available
        if CUSTOMER_SEGMENTS_FILE.exists():
            segments = pd.read_parquet(CUSTOMER_SEGMENTS_FILE)
        else:
            segments = None
            
        return sales[cols], segments
    except Exception as e:
        return None, None

sales_df, segments_df = load_data()

if sales_df is None:
    st.error("Không tìm thấy dữ liệu. Vui lòng chạy pipeline dữ liệu trước!")
    st.stop()

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["Tổng Quan", "Phân Khúc Khách Hàng", "Dự Báo Nhu Cầu"])

# --- TAB 1: OVERVIEW ---
with tab1:
    st.header("Tổng Quan Kinh Doanh")
    
    # KPIs
    total_revenue = sales_df['TotalValue'].sum()
    total_orders = sales_df['InvoiceDate'].nunique()
    total_customers = sales_df['CustomerID'].nunique()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng Doanh Thu", f"${total_revenue:,.0f}")
    col2.metric("Tổng Đơn Hàng", f"{total_orders:,}")
    col3.metric("Tổng Khách Hàng", f"{total_customers:,}")
    
    # Top Products
    st.subheader("Top Sản Phẩm theo Doanh Thu")
    top_products = sales_df.groupby('Description')['TotalValue'].sum().nlargest(10).reset_index()
    fig_prod = px.bar(top_products, x='TotalValue', y='Description', orientation='h', title="Top 10 Sản Phẩm")
    st.plotly_chart(fig_prod, use_container_width=True)
    
    # Sales over time
    st.subheader("Xu Hướng Bán Hàng")
    sales_daily = sales_df.set_index('InvoiceDate').resample('D')['TotalValue'].sum().reset_index()
    fig_trend = px.line(sales_daily, x='InvoiceDate', y='TotalValue', title="Doanh Thu Theo Ngày")
    st.plotly_chart(fig_trend, use_container_width=True)

# --- TAB 2: SEGMENTATION ---
with tab2:
    st.header("Phân Khúc Khách Hàng (RFM)")
    if segments_df is not None:
        st.write("Phân Bố Khách Hàng Hiện Tại:")
        
        seg_counts = segments_df['Segment'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Count']
        
        fig_seg = px.pie(seg_counts, values='Count', names='Segment', title="Phân Bố Phân Khúc Khách Hàng", hole=0.4)
        st.plotly_chart(fig_seg, use_container_width=True)
        
        # Segment Details
        selected_seg = st.selectbox("Chọn Phân Khúc để Xem Chi Tiết", segments_df['Segment'].unique())
        st.dataframe(segments_df[segments_df['Segment'] == selected_seg].head(100))
    else:
        st.warning("Không tìm thấy file phân khúc khách hàng. Hãy chạy `python -m src.features.rfm`.")

# --- TAB 3: FORECASTING ---
with tab3:
    st.header("Dự Báo Nhu Cầu Hàng Tuần")
    
    forecast_file = FORECAST_OUTPUTS_DIR / "demand_forecast_next_week.csv"
    if forecast_file.exists():
        forecasts = pd.read_csv(forecast_file)
        st.success(f"Dự báo được tạo cho tuần: {forecasts['Forecast_Week'].iloc[0]}")
        
        st.dataframe(forecasts.head())
        
        # Download
        csv = forecasts.to_csv(index=False).encode('utf-8')
        st.download_button("Tải Xuống CSV Dự Báo", csv, "forecast_output.csv", "text/csv")
    else:
        st.info("Chưa có dự báo nào được tạo. Hãy chạy `python -m src.models.predict`.")
