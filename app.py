import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime, date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="GoKwik Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main { background: linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%); }
.block-container { padding: 1.5rem 2rem; max-width: 100%; }

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 8px 16px rgba(0,0,0,.1);
    text-align: center;
}
.metric-value {
    font-size: 34px;
    font-weight: 700;
    color: #667eea;
}
.metric-label {
    font-size: 13px;
    color: #555;
    letter-spacing: 1.2px;
}

.section-header {
    font-size: 22px;
    font-weight: 700;
    margin: 35px 0 20px;
    padding: 14px 20px;
    border-left: 6px solid #667eea;
    background: white;
    border-radius: 12px;
    box-shadow: 0 5px 12px rgba(0,0,0,.08);
}

.js-plotly-plot {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,.08);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#667eea 0%,#764ba2 100%);
}
[data-testid="stSidebar"] * { color: white !important; }

.stButton>button {
    background: linear-gradient(135deg,#667eea,#764ba2);
    color: white;
    border-radius: 8px;
    font-weight: 600;
}
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
DATA_FILE = f"{DATA_DIR}/latest.parquet"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- HELPERS ----------------
@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_parquet(DATA_FILE) if os.path.exists(DATA_FILE) else None

def read_file(file):
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

def save_data(df):
    df.to_parquet(DATA_FILE, index=False)

def metric_card(label, value):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

# ---------------- HEADER ----------------
st.markdown("""
<div style="background:linear-gradient(135deg,#667eea,#764ba2);
padding:28px;border-radius:16px;color:white;text-align:center;
box-shadow:0 8px 18px rgba(0,0,0,.25);margin-bottom:30px;">
<h1>📊 GoKwik Order Analytics Dashboard</h1>
<p>Campaign • Payment • Revenue Insights</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### 📁 Upload Order Report")
    uploaded_file = st.file_uploader("CSV / Excel", type=["csv", "xlsx"])

# ---------------- LOAD / INGEST ----------------
if uploaded_file:
    df = read_file(uploaded_file)
    df.columns = df.columns.str.strip()

    df["Order Date"] = pd.to_datetime(df["Created At"], errors="coerce")
    df = df[df["Order Date"].notna()]
    df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors="coerce").fillna(0)
    df["Payment Type"] = df["Payment Method"].astype(str).str.upper().apply(
        lambda x: "COD" if "COD" in x else "Prepaid"
    )

    save_data(df)
    st.sidebar.success("✅ File processed")

else:
    df = load_data()
    if df is None:
        st.info("Upload a file to start")
        st.stop()

# ---------------- FILTERS ----------------
with st.sidebar:
    st.markdown("### 🔍 Filters")

    date_range = st.date_input(
        "Date Range",
        [df["Order Date"].min().date(), df["Order Date"].max().date()]
    )

    payment_filter = st.multiselect(
        "Payment Type", ["Prepaid", "COD"], ["Prepaid", "COD"]
    )

filtered = df[
    (df["Order Date"].dt.date >= date_range[0]) &
    (df["Order Date"].dt.date <= date_range[1]) &
    (df["Payment Type"].isin(payment_filter))
]

# ---------------- KPIs ----------------
st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

c1.markdown(metric_card("Orders", f"{filtered['Order Number'].nunique():,}"), unsafe_allow_html=True)
c2.markdown(metric_card("Revenue", f"₹{filtered['Grand Total'].sum():,.0f}"), unsafe_allow_html=True)
c3.markdown(metric_card("AOV", f"₹{filtered['Grand Total'].mean():,.0f}"), unsafe_allow_html=True)
c4.markdown(metric_card("COD %", f"{(filtered[filtered['Payment Type']=='COD'].shape[0]/len(filtered)*100 if len(filtered)>0 else 0):.1f}%"), unsafe_allow_html=True)

# ---------------- TOP 10 CAMPAIGNS (TOGGLE) ----------------
st.markdown('<div class="section-header">🎯 Top 10 Campaign Performance</div>', unsafe_allow_html=True)

if "Utm Campaign" in filtered.columns:

    t1, t2 = st.columns(2)
    metric_toggle = t1.radio("Metric", ["Revenue", "Orders"], horizontal=True)
    payment_toggle = t2.radio("Payment", ["All", "Prepaid", "COD"], horizontal=True)

    df_c = filtered if payment_toggle == "All" else filtered[filtered["Payment Type"] == payment_toggle]

    camp = df_c.groupby("Utm Campaign").agg(
        Orders=("Order Number", "count"),
        Revenue=("Grand Total", "sum")
    ).reset_index()

    if metric_toggle == "Revenue":
        camp = camp.sort_values("Revenue").tail(10)
        x = camp["Revenue"]
        txt = [f"₹{v:,.0f}" for v in x]
        xlab = "Revenue (₹)"
        scale = "Sunset"
    else:
        camp = camp.sort_values("Orders").tail(10)
        x = camp["Orders"]
        txt = x
        xlab = "Orders"
        scale = "Viridis"

    fig = go.Figure(go.Bar(
        x=x,
        y=camp["Utm Campaign"],
        orientation="h",
        marker=dict(color=x, colorscale=scale),
        text=txt,
        textposition="outside"
    ))

    fig.update_layout(
        title=f"Top 10 Campaigns by {metric_toggle} ({payment_toggle})",
        height=450,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title=xlab
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("GoKwik Analytics Dashboard • Streamlit + Plotly")
