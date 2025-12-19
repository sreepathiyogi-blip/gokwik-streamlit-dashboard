import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import date, datetime, timedelta
import hashlib
import io

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="GoKwik Analytics Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: transform 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 5px 0;
    }
    
    .metric-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .metric-delta {
        font-size: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }
    
    .delta-pos { color: #10b981; background: #ecfdf5; padding: 2px 8px; border-radius: 10px; display: inline-block; margin-top: 5px;}
    .delta-neg { color: #ef4444; background: #fef2f2; padding: 2px 8px; border-radius: 10px; display: inline-block; margin-top: 5px;}
    
    /* Headers */
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #333;
        margin: 30px 0 20px 0;
        padding-left: 15px;
        border-left: 5px solid #667eea;
    }

    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(118, 75, 162, 0.4);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Streamlit overrides */
    div.block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
DATA_FILE = f"{DATA_DIR}/latest.parquet"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- HELPERS ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_parquet(DATA_FILE)
    return None

def save_data(df):
    df["__last_updated__"] = date.today()
    df.to_parquet(DATA_FILE, index=False)

def read_file(file):
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

def get_city_tier(pincode):
    if pd.isna(pincode): return 'Unknown'
    s = str(pincode).strip()[:3]
    try: prefix = int(s)
    except: return 'Unknown'
    
    # Simplified Tier Mapping (Expand as needed)
    tier_1 = [110, 400, 401, 560, 600, 700, 500, 380, 411] 
    if prefix in tier_1: return 'Tier 1'
    if 100 <= prefix <= 999: return 'Tier 2/3' # Catch-all for logic brevity
    return 'Unknown'

def create_metric_card(label, value, previous_value=None, prefix="", suffix=""):
    delta_html = ""
    if previous_value is not None and previous_value != 0:
        pct_change = ((value - previous_value) / previous_value) * 100
        color_class = "delta-pos" if pct_change >= 0 else "delta-neg"
        arrow = "↑" if pct_change >= 0 else "↓"
        delta_html = f'<div class="{color_class}">{arrow} {abs(pct_change):.1f}% vs prev</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {delta_html}
    </div>
    """

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# ---------------- HEADER ----------------
st.markdown("""
<div class="main-header">
    <h1>🚀 GoKwik Intelligence Dashboard</h1>
    <p style="opacity: 0.8; margin-top: -10px;">Advanced Order & Marketing Analytics</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/263/263142.png", width=50)
    st.title("Settings")
    
    uploaded_file = st.file_uploader("📂 Upload Data", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            df = read_file(uploaded_file)
            # Normalize Columns
            df.columns = df.columns.str.strip().str.title()
            
            # Map common variations to standard names
            col_map = {
                'Created At': 'Order Date', 'Date': 'Order Date',
                'Total': 'Grand Total', 'Amount': 'Grand Total',
                'Status': 'Status', 'Merchant Order Status': 'Status',
                'Payment Method': 'Payment Method'
            }
            df = df.rename(columns=col_map)
            
            # Validation
            req_cols = ['Order Date', 'Grand Total', 'Status']
            if not all(col in df.columns for col in req_cols):
                st.error(f"Missing columns. Need: {req_cols}")
            else:
                # Processing
                df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors='coerce')
                df = df.dropna(subset=["Order Date"])
                df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors='coerce').fillna(0)
                
                # Payment Logic
                if "Payment Method" in df.columns:
                    df["Payment Type"] = df["Payment Method"].astype(str).str.upper().apply(
                        lambda x: "COD" if "COD" in x else "Prepaid"
                    )
                else:
                    df["Payment Type"] = "Unknown"

                # City Tier
                pincode_col = next((c for c in df.columns if 'Pincode' in c), None)
                if pincode_col:
                    df["City Tier"] = df[pincode_col].apply(get_city_tier)
                else:
                    df["City Tier"] = "Unknown"

                save_data(df)
                st.success("Data processed!")
                
        except Exception as e:
            st.error(f"Error parsing file: {e}")

# ---------------- LOAD & FILTER DATA ----------------
df = load_data()
if df is None:
    st.info("👋 Welcome! Please upload your Order Report (CSV/Excel) in the sidebar to begin.")
    st.stop()

with st.sidebar:
    st.markdown("---")
    st.subheader("🔍 Filters")
    
    # Date Presets
    date_preset = st.selectbox(
        "Date Preset", 
        ["Custom", "Last 7 Days", "Last 30 Days", "This Month", "Last Month", "All Time"],
        index=2
    )
    
    today = date.today()
    if date_preset == "Last 7 Days":
        start_date = today - timedelta(days=7)
        end_date = today
    elif date_preset == "Last 30 Days":
        start_date = today - timedelta(days=30)
        end_date = today
    elif date_preset == "This Month":
        start_date = today.replace(day=1)
        end_date = today
    elif date_preset == "Last Month":
        last_month_end = today.replace(day=1) - timedelta(days=1)
        start_date = last_month_end.replace(day=1)
        end_date = last_month_end
    elif date_preset == "All Time":
        start_date = df["Order Date"].min().date()
        end_date = df["Order Date"].max().date()
    else:
        start_date = df["Order Date"].min().date()
        end_date = df["Order Date"].max().date()

    if date_preset == "Custom":
        date_range = st.date_input("Select Range", [start_date, end_date])
        if len(date_range) == 2:
            start_date, end_date = date_range

    # Status Filter
    all_statuses = df["Status"].unique().tolist()
    sel_status = st.multiselect("Status", all_statuses, default=all_statuses)
    
    # Apply
    mask = (
        (df["Order Date"].dt.date >= start_date) & 
        (df["Order Date"].dt.date <= end_date) &
        (df["Status"].isin(sel_status))
    )
    filtered = df[mask]
    
    # Previous Period Logic (Simple implementation)
    days_diff = (end_date - start_date).days
    prev_start = start_date - timedelta(days=days_diff)
    prev_end = start_date - timedelta(days=1)
    prev_mask = (
        (df["Order Date"].dt.date >= prev_start) & 
        (df["Order Date"].dt.date <= prev_end) &
        (df["Status"].isin(sel_status))
    )
    prev_df = df[prev_mask]

# ---------------- KPIS ----------------
st.markdown('<div class="section-header">📈 Business Pulse</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)

# Calculate Metrics
curr_rev = filtered["Grand Total"].sum()
prev_rev = prev_df["Grand Total"].sum()

curr_orders = len(filtered)
prev_orders = len(prev_df)

curr_aov = curr_rev / curr_orders if curr_orders > 0 else 0
prev_aov = prev_rev / prev_orders if prev_orders > 0 else 0

prepaid_pct = (len(filtered[filtered["Payment Type"]=="Prepaid"]) / curr_orders * 100) if curr_orders else 0
prev_prepaid_pct = (len(prev_df[prev_df["Payment Type"]=="Prepaid"]) / prev_orders * 100) if prev_orders else 0

success_mask = filtered["Status"].str.contains("Confirmed|Delivered|Shipped", case=False, na=False)
success_rate = (len(filtered[success_mask]) / curr_orders * 100) if curr_orders else 0
# Simplified prev success rate calc for UI speed
prev_success_rate = 0 

with k1: st.markdown(create_metric_card("Total Revenue", f"{curr_rev:,.0f}", prev_rev, "₹"), unsafe_allow_html=True)
with k2: st.markdown(create_metric_card("Total Orders", f"{curr_orders:,}", prev_orders), unsafe_allow_html=True)
with k3: st.markdown(create_metric_card("AOV", f"{curr_aov:,.0f}", prev_aov, "₹"), unsafe_allow_html=True)
with k4: st.markdown(create_metric_card("Prepaid Share", f"{prepaid_pct:.1f}", prev_prepaid_pct, "", "%"), unsafe_allow_html=True)
with k5: st.markdown(create_metric_card("Success Rate", f"{success_rate:.1f}", None, "", "%"), unsafe_allow_html=True)

# ---------------- CHARTS ROW 1 ----------------
st.markdown('<div class="section-header">📊 Trends & Geography</div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])

with c1:
    # Auto-aggregate based on range duration
    if (end_date - start_date).days > 30:
        rule = 'W' # Weekly
        label_fmt = "%d %b"
    else:
        rule = 'D' # Daily
        label_fmt = "%d %b"
        
    trend = filtered.set_index("Order Date").resample(rule).agg(
        {"Grand Total": "sum", "Status": "count"}
    ).rename(columns={"Status": "Orders"})
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=trend.index, y=trend["Grand Total"], name="Revenue", marker_color="#667eea", opacity=0.8),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=trend.index, y=trend["Orders"], name="Orders", line=dict(color="#fbbf24", width=3)),
        secondary_y=True
    )
    fig.update_layout(
        title="Revenue & Order Trend",
        height=400,
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    fig.update_yaxes(title_text="Revenue (₹)", showgrid=True, gridcolor='#f0f0f0', secondary_y=False)
    fig.update_yaxes(title_text="Orders", showgrid=False, secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    if "City Tier" in filtered.columns:
        tier_grp = filtered.groupby("City Tier")["Grand Total"].sum().reset_index()
        fig = px.pie(
            tier_grp, values="Grand Total", names="City Tier", 
            title="Revenue by City Tier",
            color_discrete_sequence=px.colors.sequential.RdBu,
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pincode data missing for City Tier analysis")

# ---------------- MARKETING / UTM ANALYSIS ----------------
st.markdown('<div class="section-header">📢 Marketing Performance (Source > Medium > Campaign)</div>', unsafe_allow_html=True)

# Check for UTM columns (Case insensitive check)
utm_cols = {col.lower(): col for col in filtered.columns}
has_source = 'utm source' in utm_cols
has_medium = 'utm medium' in utm_cols
has_campaign = 'utm campaign' in utm_cols

if has_source:
    src_col = utm_cols['utm source']
    med_col = utm_cols.get('utm medium', None)
    cmp_col = utm_cols.get('utm campaign', None)
    
    # 1. SUNBURST CHART (The Upgrade)
    st.subheader("Hierarchy Analysis")
    st.caption("Drill Down: Click inner circle (Source) to see Mediums, then click Medium to see Campaigns.")
    
    path_cols = [src_col]
    if med_col: path_cols.append(med_col)
    if cmp_col: path_cols.append(cmp_col)
    
    # Handle missing values for cleaner chart
    utm_df = filtered.copy()
    for c in path_cols:
        utm_df[c] = utm_df[c].fillna("Direct/None")
    
    sunburst_data = utm_df.groupby(path_cols)["Grand Total"].sum().reset_index()
    
    fig = px.sunburst(
        sunburst_data,
        path=path_cols,
        values='Grand Total',
        color='Grand Total',
        color_continuous_scale='RdPu',
        maxdepth=3
    )
    fig.update_layout(height=500, margin=dict(t=0, l=0, r=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. DETAILED TABLE
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Detailed Campaign Performance")
        agg_cols = [c for c in path_cols if c]
        
        tbl_data = utm_df.groupby(agg_cols).agg(
            Orders=('Status', 'count'),
            Revenue=('Grand Total', 'sum'),
            Avg_Order_Value=('Grand Total', 'mean')
        ).reset_index()
        
        tbl_data = tbl_data.sort_values("Revenue", ascending=False)
        
        st.dataframe(
            tbl_data.style.format({
                "Revenue": "₹{:,.0f}", 
                "Avg_Order_Value": "₹{:,.0f}"
            }).background_gradient(subset=["Revenue"], cmap="Purples"),
            use_container_width=True,
            height=400
        )
    
    with col2:
        st.subheader("Top 5 Sources")
        top_src = utm_df.groupby(src_col)["Grand Total"].sum().nlargest(5).sort_values()
        fig = px.bar(
            x=top_src.values,
            y=top_src.index,
            orientation='h',
            text_auto='.2s',
            labels={'x': 'Revenue', 'y': 'Source'}
        )
        fig.update_traces(marker_color='#667eea')
        fig.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("UTM Source column not found in data. Please ensure column is named 'Utm Source'.")


# ---------------- DATA EXPORT ----------------
st.markdown('<div class="section-header">⬇️ Export Data</div>', unsafe_allow_html=True)
e1, e2 = st.columns(2)

with e1:
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv,
        f"analytics_data_{date.today()}.csv",
        "text/csv",
        key='download-csv',
        use_container_width=True
    )

with e2:
    # Excel Export Engine
    try:
        excel_data = convert_df_to_excel(filtered)
        st.download_button(
            "📊 Download Excel (.xlsx)",
            excel_data,
            f"analytics_data_{date.today()}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key='download-excel',
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Excel export failed (Install xlsxwriter): {e}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; color:#888;">
    GoKwik Analytics Dashboard | Last Updated: {datetime.now().strftime('%d %b %Y %H:%M')}
</div>
""", unsafe_allow_html=True)
