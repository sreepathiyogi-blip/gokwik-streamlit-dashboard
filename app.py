import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import date, datetime, timedelta
import io

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="GoKwik Analytics Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- PROFESSIONAL CSS THEME ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Global Settings */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background */
    .stApp {
        background-color: #f8f9fc;
    }

    /* Top Navigation Bar Style */
    .dashboard-header {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
        border-bottom: 3px solid #4f46e5;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .dashboard-title {
        color: #1e293b;
        font-size: 28px;
        font-weight: 800;
        margin: 0;
    }
    
    .dashboard-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-top: 5px;
    }

    /* Metric Cards */
    .metric-container {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }

    .metric-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
        border-color: #4f46e5;
    }

    .metric-label {
        color: #64748b;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #1e293b;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .metric-delta {
        font-size: 13px;
        font-weight: 500;
        margin-top: 12px;
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 99px;
    }
    
    .delta-pos { background-color: #dcfce7; color: #166534; }
    .delta-neg { background-color: #fee2e2; color: #991b1b; }

    /* Section Headers */
    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: #334155;
        margin: 30px 0 20px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .section-header::before {
        content: "";
        display: block;
        width: 6px;
        height: 24px;
        background: linear-gradient(to bottom, #4f46e5, #818cf8);
        border-radius: 3px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Remove default Streamlit top padding */
    .block-container {
        padding-top: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = f"{DATA_DIR}/latest.parquet"

@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_parquet(DATA_FILE)
    return None

def save_data(df):
    df.to_parquet(DATA_FILE, index=False)

def read_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def create_metric_card(label, value, previous_value=None, prefix="", suffix=""):
    delta_html = ""
    if previous_value is not None and previous_value != 0:
        pct_change = ((value - previous_value) / previous_value) * 100
        color_class = "delta-pos" if pct_change >= 0 else "delta-neg"
        arrow = "↑" if pct_change >= 0 else "↓"
        delta_html = f'<div class="metric-delta {color_class}">{arrow} {abs(pct_change):.1f}%</div>'
    
    return f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {delta_html}
    </div>
    """

def convert_df_to_excel(df):
    output = io.BytesIO()
    # Fallback to csv if xlsxwriter is missing, though pandas usually handles it
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
    except:
        return df.to_csv(index=False).encode('utf-8')
    return output.getvalue()

# ---------------- HEADER ----------------
st.markdown("""
<div class="dashboard-header">
    <div>
        <h1 class="dashboard-title">GoKwik Analytics Pro</h1>
        <div class="dashboard-subtitle">Real-time Order & Marketing Intelligence</div>
    </div>
    <div style="font-size: 24px;">📊</div>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.subheader("⚙️ Data Configuration")
    uploaded_file = st.file_uploader("Upload Report", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            df = read_file(uploaded_file)
            # Normalize Columns
            df.columns = df.columns.str.strip().str.title()
            
            # Smart Renaming
            col_map = {
                'Created At': 'Order Date', 'Date': 'Order Date',
                'Total': 'Grand Total', 'Amount': 'Grand Total',
                'Merchant Order Status': 'Status',
                'Utm_Source': 'Utm Source', 'Utm_Medium': 'Utm Medium', 'Utm_Campaign': 'Utm Campaign'
            }
            df = df.rename(columns=col_map)
            
            # Validation
            if 'Order Date' in df.columns:
                df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors='coerce')
                df = df.dropna(subset=["Order Date"])
                df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors='coerce').fillna(0)
                
                # Payment Type Logic
                if "Payment Method" in df.columns:
                    df["Payment Type"] = df["Payment Method"].astype(str).str.upper().apply(
                        lambda x: "COD" if "COD" in x else "Prepaid"
                    )
                else:
                    df["Payment Type"] = "Unknown"

                save_data(df)
                st.success("✅ Data processed successfully")
            else:
                st.error("❌ 'Order Date' column missing.")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- MAIN LOGIC ----------------
df = load_data()

if df is None:
    st.info("👋 Please upload a CSV or Excel file to generate the dashboard.")
    st.stop()

# --- FILTERS ---
with st.sidebar:
    st.divider()
    st.subheader("🔍 Filters")
    
    # Date Filter
    date_preset = st.selectbox(
        "Time Period", 
        ["Last 7 Days", "Last 30 Days", "This Month", "Last Month", "All Time", "Custom"],
        index=1
    )
    
    today = date.today()
    if date_preset == "Last 7 Days":
        start_date, end_date = today - timedelta(days=7), today
    elif date_preset == "Last 30 Days":
        start_date, end_date = today - timedelta(days=30), today
    elif date_preset == "This Month":
        start_date, end_date = today.replace(day=1), today
    elif date_preset == "Last Month":
        last_month_end = today.replace(day=1) - timedelta(days=1)
        start_date, end_date = last_month_end.replace(day=1), last_month_end
    elif date_preset == "All Time":
        start_date, end_date = df["Order Date"].min().date(), df["Order Date"].max().date()
    else:
        d = st.date_input("Select Range", [df["Order Date"].min(), df["Order Date"].max()])
        start_date, end_date = (d[0], d[1]) if len(d) == 2 else (d[0], d[0])

    # Status Filter
    statuses = df["Status"].unique().tolist()
    selected_status = st.multiselect("Order Status", statuses, default=statuses)

    # Filter Data
    mask = (df["Order Date"].dt.date >= start_date) & (df["Order Date"].dt.date <= end_date) & (df["Status"].isin(selected_status))
    filtered = df[mask]

    # Prev Data (for deltas)
    duration = (end_date - start_date).days
    prev_mask = (df["Order Date"].dt.date >= start_date - timedelta(days=duration)) & \
                (df["Order Date"].dt.date < start_date) & \
                (df["Status"].isin(selected_status))
    prev_df = df[prev_mask]

# ---------------- KPI CARDS ----------------
st.markdown('<div class="section-header">Business Overview</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

# Metrics Calculation
curr_rev = filtered["Grand Total"].sum()
prev_rev = prev_df["Grand Total"].sum()
curr_orders = len(filtered)
prev_orders = len(prev_df)
curr_aov = curr_rev / curr_orders if curr_orders else 0
prev_aov = prev_rev / prev_orders if prev_orders else 0

prepaid_count = len(filtered[filtered["Payment Type"] == "Prepaid"])
prepaid_share = (prepaid_count / curr_orders * 100) if curr_orders else 0
prev_prepaid_share = (len(prev_df[prev_df["Payment Type"] == "Prepaid"]) / prev_orders * 100) if prev_orders else 0

with col1: st.markdown(create_metric_card("Total Revenue", f"{curr_rev/100000:.2f}L", prev_rev/100000, "₹"), unsafe_allow_html=True)
with col2: st.markdown(create_metric_card("Total Orders", f"{curr_orders:,}", prev_orders), unsafe_allow_html=True)
with col3: st.markdown(create_metric_card("AOV", f"{curr_aov:,.0f}", prev_aov, "₹"), unsafe_allow_html=True)
with col4: st.markdown(create_metric_card("Prepaid %", f"{prepaid_share:.1f}", prev_prepaid_share, "", "%"), unsafe_allow_html=True)
with col5: st.markdown(create_metric_card("Return on Ad Spend", "3.2", 2.8, "x"), unsafe_allow_html=True) # Placeholder

# ---------------- CHARTS ROW 1 ----------------
st.markdown('<div class="section-header">Performance Trends</div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])

with c1:
    # Aggregation
    freq = 'D' if (end_date - start_date).days <= 60 else 'W'
    trend = filtered.set_index("Order Date").resample(freq).agg({"Grand Total": "sum", "Status": "count"}).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Elegant Area Chart for Revenue
    fig.add_trace(
        go.Scatter(
            x=trend["Order Date"], y=trend["Grand Total"], name="Revenue",
            fill='tozeroy', line=dict(color='#4f46e5', width=2),
            marker=dict(size=1), fillcolor='rgba(79, 70, 229, 0.1)'
        ), secondary_y=False
    )
    
    # Line Chart for Orders
    fig.add_trace(
        go.Scatter(
            x=trend["Order Date"], y=trend["Status"], name="Orders",
            line=dict(color='#f59e0b', width=2, dash='dot'), marker=dict(size=4)
        ), secondary_y=True
    )
    
    fig.update_layout(
        title="Revenue & Order Volume", title_font_size=16,
        hovermode="x unified", plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", y=1.1, x=0)
    )
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9', secondary_y=False)
    fig.update_yaxes(showgrid=False, secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    if "Payment Type" in filtered.columns:
        pie_data = filtered["Payment Type"].value_counts().reset_index()
        pie_data.columns = ["Type", "Count"]
        
        fig = px.pie(
            pie_data, values="Count", names="Type", 
            title="Payment Split",
            color_discrete_sequence=['#4f46e5', '#a5b4fc'],
            hole=0.6
        )
        fig.update_layout(plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

# ---------------- UTM ANALYSIS ----------------
st.markdown('<div class="section-header">Marketing Attribution (Source > Medium > Campaign)</div>', unsafe_allow_html=True)

# Normalize column names to check existence
cols_lower = {c.lower(): c for c in filtered.columns}
has_source = 'utm source' in cols_lower

if has_source:
    src_col = cols_lower['utm source']
    med_col = cols_lower.get('utm medium', None)
    camp_col = cols_lower.get('utm campaign', None)
    
    tab1, tab2 = st.tabs(["📊 Hierarchy View", "📋 Detailed Data"])
    
    with tab1:
        # Hierarchy Chart
        path = [c for c in [src_col, med_col, camp_col] if c]
        
        # Fill NaNs to prevent chart breakage
        sunburst_df = filtered.copy()
        for c in path:
            sunburst_df[c] = sunburst_df[c].fillna("Direct/Unknown")
            
        sb_data = sunburst_df.groupby(path)["Grand Total"].sum().reset_index()
        
        fig = px.sunburst(
            sb_data, path=path, values='Grand Total',
            color='Grand Total', color_continuous_scale='Indigo',
            maxdepth=2
        )
        fig.update_layout(height=500, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        # Table View - THIS FIXES THE CRASH
        agg_cols = [c for c in [src_col, med_col, camp_col] if c]
        
        tbl_data = filtered.groupby(agg_cols).agg(
            Orders=('Status', 'count'),
            Revenue=('Grand Total', 'sum'),
            AOV=('Grand Total', 'mean')
        ).reset_index().sort_values("Revenue", ascending=False)
        
        # We use Streamlit's native column_config instead of pandas style (No Matplotlib needed)
        st.dataframe(
            tbl_data,
            use_container_width=True,
            column_config={
                "Revenue": st.column_config.ProgressColumn(
                    "Revenue",
                    format="₹%d",
                    min_value=0,
                    max_value=int(tbl_data["Revenue"].max()),
                ),
                "AOV": st.column_config.NumberColumn(
                    "Avg Order Value",
                    format="₹%d"
                ),
                "Orders": st.column_config.NumberColumn(
                    "Total Orders",
                )
            },
            hide_index=True,
            height=400
        )
else:
    st.warning("UTM Source data not found. Please ensure your CSV has 'Utm Source' column.")

# ---------------- EXPORT ----------------
st.markdown("---")
col_ex1, col_ex2 = st.columns([1, 5])
with col_ex1:
    try:
        excel_data = convert_df_to_excel(filtered)
        file_ext = "xlsx" if isinstance(excel_data, bytes) else "csv"
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file_ext == "xlsx" else "text/csv"
        
        st.download_button(
            label="📥 Download Report",
            data=excel_data,
            file_name=f"Report_{datetime.now().strftime('%Y%m%d')}.{file_ext}",
            mime=mime_type,
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Export Error: {e}")
