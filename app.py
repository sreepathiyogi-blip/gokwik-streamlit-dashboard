import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="GoKwik Order Report",
    layout="wide"
)

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
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    else:
        st.error("Only CSV or Excel allowed")
        return None

# ---------------- UI ----------------
st.title("📊 GoKwik Order Dashboard")

uploaded_file = st.file_uploader(
    "Upload Order Report (CSV / Excel)",
    type=["csv", "xlsx"]
)

# ---------------- UPLOAD PROCESS ----------------
if uploaded_file:
    df = read_file(uploaded_file)

    if df is not None:
        df.columns = df.columns.str.strip()

        REQUIRED_COLUMNS = [
            "Order ID",
            "Order Date",
            "GMV",
            "Status",
            "Payment Method"
        ]

        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            # Cleaning
            df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
            df["GMV"] = pd.to_numeric(df["GMV"], errors="coerce")

            # 🔥 PAYMENT LOGIC
            df["Payment Method"] = df["Payment Method"].astype(str).str.upper().str.strip()
            df["Payment Type"] = df["Payment Method"].apply(
                lambda x: "COD" if "COD" in x else "Prepaid"
            )

            save_data(df)
            st.success("✅ Data uploaded, cleaned & payment logic applied")

# ---------------- LOAD LATEST ----------------
df = load_data()

if df is None:
    st.info("⬆ Upload a file to see the dashboard")
    st.stop()

# ---------------- METRICS ----------------
st.subheader("📌 Key Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Orders", df["Order ID"].nunique())
c2.metric("Total GMV", f"₹{df['GMV'].sum():,.0f}")
c3.metric("Prepaid Orders", df[df["Payment Type"] == "Prepaid"].shape[0])
c4.metric("COD Orders", df[df["Payment Type"] == "COD"].shape[0])

# ---------------- DAILY TREND ----------------
st.subheader("📈 Daily GMV Trend")

daily = (
    df.groupby(df["Order Date"].dt.date)["GMV"]
    .sum()
    .reset_index()
)

fig = px.line(daily, x="Order Date", y="GMV", markers=True)
st.plotly_chart(fig, use_container_width=True)

# ---------------- TABLE ----------------
st.subheader("📋 Order Level Data")
st.dataframe(
    df.drop(columns=["__last_updated__"]),
    use_container_width=True
)

# ---------------- FOOTER ----------------
st.caption("🔄 Auto-updates daily | COD vs Prepaid logic applied")
