import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import date, datetime
import hashlib

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="GoKwik Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= DATA PATH =================
DATA_DIR = "data"
DATA_FILE = f"{DATA_DIR}/latest.parquet"
os.makedirs(DATA_DIR, exist_ok=True)

# ================= HELPERS =================
@st.cache_data(show_spinner=False)
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_parquet(DATA_FILE)
        except:
            df = pd.read_csv(DATA_FILE.replace(".parquet", ".csv"))
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
        return df
    return None

def save_data(df):
    try:
        df.to_parquet(DATA_FILE, index=False)
    except:
        df.to_csv(DATA_FILE.replace(".parquet", ".csv"), index=False)

def read_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def hash_value(val):
    return hashlib.md5(str(val).encode()).hexdigest()[:8]

# ================= HEADER =================
st.markdown("""
<div style="background:linear-gradient(135deg,#667eea,#764ba2);
padding:25px;border-radius:15px;color:white;text-align:center;">
<h1>📊 GoKwik Order Analytics Dashboard</h1>
<p>Performance • Payments • Customers • RFM</p>
</div>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader(
        "Upload Order Report",
        type=["csv", "xlsx"]
    )

# ================= UPLOAD =================
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

    df["Order Date"] = pd.to_datetime(df["Created At"], errors="coerce")
    df = df[df["Order Date"].notna()].copy()

    df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors="coerce").fillna(0)
    df["Status"] = df["Merchant Order Status"].astype(str)
    df["Payment Method"] = df["Payment Method"].astype(str).str.upper()
    df["Payment Type"] = df["Payment Method"].apply(
        lambda x: "COD" if "COD" in x else "Prepaid"
    )

    if "Customer Phone" in df.columns:
        df["Customer ID"] = df["Customer Phone"].apply(hash_value)

    save_data(df)
    st.sidebar.success(f"Loaded {len(df):,} orders")

# ================= LOAD =================
if not uploaded_file:
    df = load_data()
    if df is None:
        st.info("Upload a file to start")
        st.stop()

# ================= FILTERS =================
with st.sidebar:
    st.header("🔍 Filters")

    min_d, max_d = df["Order Date"].min().date(), df["Order Date"].max().date()
    date_range = st.date_input("Date Range", [min_d, max_d])

    status_filter = st.multiselect(
        "Order Status",
        df["Status"].unique(),
        default=df["Status"].unique()
    )

    payment_filter = st.multiselect(
        "Payment Type",
        ["Prepaid", "COD"],
        default=["Prepaid", "COD"]
    )

filtered = df[
    (df["Order Date"].dt.date >= date_range[0]) &
    (df["Order Date"].dt.date <= date_range[1]) &
    (df["Status"].isin(status_filter)) &
    (df["Payment Type"].isin(payment_filter))
].copy()

if filtered.empty:
    st.warning("No data for selected filters")
    st.stop()

# ================= KPI =================
st.markdown("## 📈 Key Metrics")
c1, c2, c3, c4, c5 = st.columns(5)

total_orders = filtered["Order Number"].nunique()
revenue = filtered["Grand Total"].sum()
aov = revenue / total_orders if total_orders else 0
prepaid = filtered[filtered["Payment Type"] == "Prepaid"].shape[0]
cod = filtered[filtered["Payment Type"] == "COD"].shape[0]

c1.metric("Total Orders", f"{total_orders:,}")
c2.metric("Revenue", f"₹{revenue:,.0f}")
c3.metric("AOV", f"₹{aov:,.0f}")
c4.metric("Prepaid Orders", prepaid)
c5.metric("COD Orders", cod)

# ================= TREND =================
daily = filtered.groupby(filtered["Order Date"].dt.date).agg(
    Revenue=("Grand Total", "sum"),
    Orders=("Order Number", "count")
).reset_index()

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(
    x=daily["Order Date"],
    y=daily["Revenue"],
    name="Revenue",
    fill="tozeroy"
), secondary_y=False)

fig.add_trace(go.Scatter(
    x=daily["Order Date"],
    y=daily["Orders"],
    name="Orders"
), secondary_y=True)

fig.update_layout(height=400, title="Revenue & Orders Trend")
st.plotly_chart(fig, use_container_width=True)

# ================= PAYMENT SPLIT =================
pay = filtered.groupby("Payment Type").size().reset_index(name="Orders")
fig = px.pie(pay, names="Payment Type", values="Orders", hole=0.5)
st.plotly_chart(fig, use_container_width=True)

# ================= RFM =================
if "Customer ID" in filtered.columns:
    rfm = filtered.groupby("Customer ID").agg(
        Recency=("Order Date", lambda x: (filtered["Order Date"].max() - x.max()).days),
        Frequency=("Order Number", "count"),
        Monetary=("Grand Total", "sum")
    ).reset_index()

    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5,4,3,2,1])
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5])

    rfm["Score"] = rfm["R_Score"].astype(int) + rfm["F_Score"].astype(int) + rfm["M_Score"].astype(int)

    def segment(s):
        if s >= 13: return "Champions"
        if s >= 10: return "Loyal"
        if s >= 7: return "Potential"
        return "At Risk"

    rfm["Segment"] = rfm["Score"].apply(segment)

    # ================= TOP CUSTOMERS (FIXED) =================
    st.markdown("## 🌟 Top 15 Customers")

    top = rfm.nlargest(15, "Monetary").copy()
    top.insert(0, "Rank", range(1, len(top) + 1))

    st.dataframe(
        top[["Rank","Customer ID","Recency","Frequency","Monetary","Segment"]]
        .rename(columns={
            "Recency":"Days Since Last Order",
            "Frequency":"Total Orders",
            "Monetary":"Total Spent"
        })
        .style.format({
            "Days Since Last Order":"{:.0f}",
            "Total Orders":"{:.0f}",
            "Total Spent":"₹{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Top Customers",
        top.to_csv(index=False),
        "top_customers.csv",
        "text/csv"
    )

# ================= FOOTER =================
st.caption("© GoKwik Analytics • Streamlit Dashboard")
