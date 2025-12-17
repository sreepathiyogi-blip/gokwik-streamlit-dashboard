import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import date

# ---------------- CONFIG ----------------
st.set_page_config("GoKwik Order Dashboard", layout="wide")

DATA_DIR = "data"
DATA_FILE = f"{DATA_DIR}/latest.parquet"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- HELPERS ----------------
@st.cache_data(show_spinner=False)
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_parquet(DATA_FILE)
    return None

def save_data(df):
    df["__last_updated__"] = date.today()
    df.to_parquet(DATA_FILE, index=False)

def read_file(file):
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

# ---------------- UI ----------------
st.title("📊 GoKwik Order Analytics Dashboard")

uploaded_file = st.file_uploader(
    "Upload GoKwik Order Report (CSV / Excel)",
    type=["csv", "xlsx"]
)

# ---------------- UPLOAD ----------------
if uploaded_file:
    df = read_file(uploaded_file)
    df.columns = df.columns.str.strip()

    REQUIRED = [
        "Order Number",
        "Created At",
        "Merchant Order Status",
        "Payment Method",
        "Grand Total"
    ]

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    # ---- CLEANING ----
    df["Order Date"] = pd.to_datetime(df["Created At"], errors="coerce")
    df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors="coerce")
    df["Status"] = df["Merchant Order Status"]
    df["Payment Method"] = df["Payment Method"].astype(str).str.upper()

    # ---- PAYMENT LOGIC ----
    df["Payment Type"] = df["Payment Method"].apply(
        lambda x: "COD" if "COD" in str(x) else "Prepaid"
    )

    save_data(df)
    st.success("✅ File processed successfully")

# ---------------- LOAD DATA ----------------
df = load_data()
if df is None:
    st.info("⬆ Upload a file to view dashboard")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Filters")

date_range = st.sidebar.date_input(
    "Order Date",
    [df["Order Date"].min(), df["Order Date"].max()]
)

status_filter = st.sidebar.multiselect(
    "Order Status",
    df["Status"].unique(),
    default=df["Status"].unique()
)

payment_filter = st.sidebar.multiselect(
    "Payment Type",
    ["Prepaid", "COD"],
    default=["Prepaid", "COD"]
)

filtered = df[
    (df["Order Date"].dt.date >= date_range[0]) &
    (df["Order Date"].dt.date <= date_range[1]) &
    (df["Status"].isin(status_filter)) &
    (df["Payment Type"].isin(payment_filter))
]

# ---------------- KPI ROW ----------------
st.subheader("📌 Key Metrics")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Orders", f"{filtered['Order Number'].nunique():,}")
c2.metric("Total Revenue", f"₹{filtered['Grand Total'].sum():,.0f}")
c3.metric("Avg Order Value", f"₹{filtered['Grand Total'].mean():,.0f}")
c4.metric("Prepaid Orders", f"{filtered[filtered['Payment Type'] == 'Prepaid'].shape[0]:,}")
c5.metric("COD Orders", f"{filtered[filtered['Payment Type'] == 'COD'].shape[0]:,}")

# ---------------- CHARTS ROW 1 ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Daily Revenue Trend")
    daily = filtered.groupby(filtered["Order Date"].dt.date).agg({
        "Grand Total": "sum",
        "Order Number": "count"
    }).reset_index()
    daily.columns = ["Order Date", "Revenue", "Orders"]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Order Date"], 
        y=daily["Revenue"],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#1f77b4', width=2)
    ))
    fig.update_layout(height=350, showlegend=False, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💳 Payment Method Split")
    payment_split = filtered.groupby("Payment Type").agg({
        "Order Number": "count",
        "Grand Total": "sum"
    }).reset_index()
    payment_split.columns = ["Payment Type", "Orders", "Revenue"]
    
    fig = px.pie(
        payment_split, 
        values="Orders", 
        names="Payment Type",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHARTS ROW 2 ----------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("🔻 Order Status Funnel")
    status_counts = filtered["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Orders"]
    
    fig = px.funnel(
        status_counts.head(5), 
        x="Orders", 
        y="Status",
        color_discrete_sequence=['#636EFA']
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("📍 Top 10 States by Orders")
    if "Billing State" in filtered.columns:
        state_data = filtered.groupby("Billing State").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        state_data.columns = ["State", "Orders", "Revenue"]
        state_data = state_data.sort_values("Orders", ascending=False).head(10)
        
        fig = px.bar(
            state_data, 
            x="Orders", 
            y="State",
            orientation='h',
            color="Orders",
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ---------------- CHARTS ROW 3 ----------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("🛍️ Top 10 Products")
    if "Product Name" in filtered.columns:
        product_data = filtered.groupby("Product Name").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        product_data.columns = ["Product", "Orders", "Revenue"]
        product_data = product_data.sort_values("Orders", ascending=False).head(10)
        
        fig = px.bar(
            product_data, 
            x="Product", 
            y="Orders",
            color="Revenue",
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=350, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("📱 UTM Source Analysis")
    if "Utm Source" in filtered.columns:
        utm_data = filtered.groupby("Utm Source").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        utm_data.columns = ["Source", "Orders", "Revenue"]
        utm_data = utm_data.sort_values("Orders", ascending=False).head(8)
        
        fig = px.bar(
            utm_data, 
            x="Source", 
            y="Orders",
            color="Orders",
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# ---------------- RTO ANALYSIS ----------------
st.subheader("⚠️ RTO Risk Analysis")
col7, col8 = st.columns(2)

with col7:
    if "RTO Risk" in filtered.columns:
        rto_risk = filtered["RTO Risk"].value_counts().reset_index()
        rto_risk.columns = ["RTO Risk", "Orders"]
        
        fig = px.bar(
            rto_risk, 
            x="RTO Risk", 
            y="Orders",
            color="Orders",
            color_continuous_scale='Oranges'
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

with col8:
    if "RTO Score" in filtered.columns:
        # RTO Score distribution
        fig = px.histogram(
            filtered, 
            x="RTO Score",
            nbins=20,
            title="RTO Score Distribution",
            color_discrete_sequence=['#FF6B6B']
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.subheader("⬇ Download Cleaned Data")

st.download_button(
    "Download CSV",
    filtered.drop(columns=["__last_updated__"], errors='ignore').to_csv(index=False),
    file_name="gokwik_cleaned_data.csv",
    mime="text/csv"
)

# ---------------- TABLE ----------------
st.subheader("📋 Order Level Data")
display_cols = [
    "Order Number", "Order Date", "Status", "Payment Method", 
    "Grand Total", "Customer Name", "Billing State", "Product Name"
]
display_cols = [col for col in display_cols if col in filtered.columns]
st.dataframe(filtered[display_cols], use_container_width=True)
