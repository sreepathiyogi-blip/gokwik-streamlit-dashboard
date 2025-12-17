import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import date, datetime
import hashlib
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="GoKwik Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- ENHANCED CUSTOM CSS ----------------
st.markdown("""
<style>
    /* Main background with subtle gradient */
    .main {
        background: linear-gradient(135deg, #f8f9fe 0%, #f0f2f7 100%);
        padding: 15px;
    }
    
    /* Block container */
    .block-container {
        max-width: 100%;
        padding: 1rem 1.5rem;
    }
    
    /* Enhanced Card styling with glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 28px 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        text-align: center;
        margin: 8px 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(102, 126, 234, 0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Metric value with gradient */
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 8px 0;
        letter-spacing: -0.5px;
    }
    
    /* Metric label */
    .metric-label {
        font-size: 11px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    
    /* Dashboard header with modern design */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 35px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40" fill="rgba(255,255,255,0.05)"/></svg>');
        opacity: 0.3;
    }
    
    .dashboard-header h1 {
        font-size: 32px;
        margin: 0;
        font-weight: 700;
        position: relative;
        z-index: 1;
    }
    
    .dashboard-header p {
        font-size: 15px;
        margin: 8px 0 0 0;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Modern Section headers */
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #1e293b;
        margin: 30px 0 18px 0;
        padding: 16px 22px;
        border-left: 4px solid #667eea;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Chart containers with better spacing */
    .js-plotly-plot {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06) !important;
        background: white !important;
        margin: 12px 0 !important;
        border: 1px solid rgba(0, 0, 0, 0.03) !important;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Sidebar modern styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    /* Enhanced button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        letter-spacing: 0.3px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Beautiful dataframe styling */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: transparent;
        padding: 8px 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        color: #64748b;
        border: 1px solid rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #667eea;
        color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-color: transparent;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* File uploader styling */
    .uploadedFile {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 12px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Success/Error messages */
    .element-container .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Spacing improvements */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .metric-card {
            padding: 18px 15px;
            min-height: 110px;
        }
        
        .metric-value {
            font-size: 26px;
        }
        
        .section-header {
            font-size: 18px;
            padding: 12px 16px;
        }
        
        .dashboard-header {
            padding: 25px 20px;
        }
        
        .dashboard-header h1 {
            font-size: 24px;
        }
    }
    
    @media (max-width: 480px) {
        .metric-card {
            padding: 14px 12px;
            min-height: 100px;
        }
        
        .metric-value {
            font-size: 22px;
        }
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
DATA_FILE = f"{DATA_DIR}/latest.parquet"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- SESSION STATE INITIALIZATION ----------------
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None
if 'filters_applied' not in st.session_state:
    st.session_state.filters_applied = False

# ---------------- HELPERS ----------------
@st.cache_data(show_spinner=False, ttl=3600)
def load_data():
    """Load data from Parquet or CSV fallback with 1-hour cache"""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_parquet(DATA_FILE)
            if "Order Date" in df.columns:
                df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
            return df
        except Exception:
            csv_file = DATA_FILE.replace('.parquet', '.csv')
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                if "Order Date" in df.columns:
                    df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
                return df
    return None

def save_data(df):
    """Save data with proper type handling for Parquet compatibility"""
    df = df.copy()
    df["__last_updated__"] = date.today()
    
    for col in df.columns:
        if df[col].dtype.name == 'category':
            df[col] = df[col].astype(str)
        elif df[col].dtype == 'object' and col not in ['Order Date', 'Payment At', 'Updated At']:
            df[col] = df[col].astype(str)
    
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
    
    try:
        df.to_parquet(DATA_FILE, index=False, engine='pyarrow')
    except Exception:
        csv_file = DATA_FILE.replace('.parquet', '.csv')
        df.to_csv(csv_file, index=False)

def read_file(file):
    """Read CSV or Excel file"""
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file, encoding='utf-8')
        else:
            return pd.read_excel(file)
    except UnicodeDecodeError:
        return pd.read_csv(file, encoding='latin-1')

def hash_customer_name(name):
    """Hash customer name for privacy"""
    if pd.isna(name):
        return "Unknown"
    return hashlib.md5(str(name).encode()).hexdigest()[:8]

def create_metric_card(label, value, delta=None, delta_color="normal"):
    """Create HTML metric card"""
    delta_html = f'<div style="color: {"#10b981" if delta_color == "normal" else "#ef4444"}; font-size: 13px; font-weight: 600; margin-top: 6px; opacity: 0.9;">{delta}</div>' if delta else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def get_city_tier(state):
    """Classify cities into tiers based on state"""
    if pd.isna(state):
        return 'Tier 3'
    
    tier_1_states = ['MAHARASHTRA', 'DELHI', 'KARNATAKA', 'TAMIL NADU', 'TELANGANA', 'WEST BENGAL', 'GUJARAT']
    tier_2_states = ['PUNJAB', 'HARYANA', 'RAJASTHAN', 'KERALA', 'MADHYA PRADESH', 'UTTAR PRADESH']
    
    state_upper = str(state).upper()
    if any(t1 in state_upper for t1 in tier_1_states):
        return 'Tier 1'
    elif any(t2 in state_upper for t2 in tier_2_states):
        return 'Tier 2'
    else:
        return 'Tier 3'

def rfm_score(series, n_bins=5, reverse=False):
    """Create RFM scores with proper error handling"""
    clean_series = series.dropna()
    
    if len(clean_series) == 0:
        return pd.Series([3] * len(series), index=series.index)
    
    unique_count = clean_series.nunique()
    actual_bins = min(n_bins, unique_count)
    
    if actual_bins < 2:
        return pd.Series([3] * len(series), index=series.index)
    
    try:
        binned = pd.qcut(clean_series, actual_bins, labels=False, duplicates='drop')
        unique_bins = int(binned.nunique())
        
        if reverse:
            actual_labels = list(range(unique_bins, 0, -1))
        else:
            actual_labels = list(range(1, unique_bins + 1))
        
        result = pd.qcut(clean_series, actual_bins, labels=actual_labels, duplicates='drop')
        return result.reindex(series.index, fill_value=actual_labels[len(actual_labels)//2])
        
    except Exception:
        try:
            if reverse:
                labels = list(range(actual_bins, 0, -1))
            else:
                labels = list(range(1, actual_bins + 1))
            
            result = pd.cut(clean_series, bins=actual_bins, labels=labels, duplicates='drop')
            return result.reindex(series.index, fill_value=labels[len(labels)//2])
        except:
            return pd.Series([3] * len(series), index=series.index)

# ---------------- HEADER ----------------
st.markdown("""
<div class="dashboard-header">
    <h1>📊 GoKwik Analytics Pro</h1>
    <p>Advanced e-commerce insights powered by real-time data analytics</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### 📁 Data Upload")
    uploaded_file = st.file_uploader(
        "Upload Order Report",
        type=["csv", "xlsx"],
        help="Upload CSV or Excel file with order data"
    )
    
    st.markdown("---")

# ---------------- UPLOAD PROCESSING ----------------
if uploaded_file:
    try:
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
            st.error(f"❌ Missing required columns: {', '.join(missing)}")
            st.stop()

        df["Order Date"] = pd.to_datetime(df["Created At"], errors="coerce", dayfirst=True)
        if "Payment At" in df.columns:
            df["Payment Date"] = pd.to_datetime(df["Payment At"], errors="coerce", dayfirst=True)
        
        invalid_dates = df["Order Date"].isna().sum()
        if invalid_dates > 0:
            st.warning(f"⚠️ Removed {invalid_dates} rows with invalid dates")
        
        df = df[df["Order Date"].notna()].copy()
        
        if len(df) == 0:
            st.error("❌ No valid data after processing")
            st.stop()
        
        df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors="coerce").fillna(0)
        if "Total Discount" in df.columns:
            df["Total Discount"] = pd.to_numeric(df["Total Discount"], errors="coerce").fillna(0)
        
        df["Status"] = df["Merchant Order Status"].astype(str)
        df["Payment Method"] = df["Payment Method"].astype(str).str.upper()
        df["Payment Type"] = df["Payment Method"].apply(
            lambda x: "COD" if "COD" in str(x) else "Prepaid"
        )
        
        df["Order Hour"] = df["Order Date"].dt.hour
        df["Order Day"] = df["Order Date"].dt.day_name()
        
        if "Customer Name" in df.columns:
            df["Customer ID"] = df["Customer Name"].apply(hash_customer_name)
        
        if "Billing State" in df.columns:
            df["City Tier"] = df["Billing State"].apply(get_city_tier)
        
        if "Payment Date" in df.columns and "Order Date" in df.columns:
            df["Payment Time (Hours)"] = (df["Payment Date"] - df["Order Date"]).dt.total_seconds() / 3600

        save_data(df)
        st.session_state.filtered_data = None
        st.session_state.filters_applied = False
        
        with st.sidebar:
            st.success(f"✅ Loaded {len(df):,} orders")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()

# ---------------- LOAD DATA ----------------
if not uploaded_file:
    df = load_data()
    if df is None:
        st.info("👆 Please upload a file to begin analysis")
        st.stop()

if "Order Date" not in df.columns:
    st.error("⚠️ Data corrupted. Please re-upload.")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    valid_dates = df[df["Order Date"].notna()]
    
    if len(valid_dates) == 0:
        st.error("No valid dates found")
        st.stop()
    
    min_date = valid_dates["Order Date"].min().date()
    max_date = valid_dates["Order Date"].max().date()
    
    with st.form(key="filters_form"):
        date_range = st.date_input(
            "Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        status_options = df["Status"].unique().tolist()
        status_filter = st.multiselect(
            "Order Status",
            status_options,
            default=status_options
        )
        
        payment_filter = st.multiselect(
            "Payment Type",
            ["Prepaid", "COD"],
            default=["Prepaid", "COD"]
        )
        
        if "City Tier" in df.columns:
            tier_filter = st.multiselect(
                "City Tier",
                ["Tier 1", "Tier 2", "Tier 3"],
                default=["Tier 1", "Tier 2", "Tier 3"]
            )
        else:
            tier_filter = []
        
        submitted = st.form_submit_button("Apply Filters", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📅 Time View")
    time_grain = st.selectbox(
        "Granularity",
        ["Daily", "Weekly", "Monthly"],
        index=0
    )
    
    st.markdown("---")
    st.markdown(f"**📊 Updated:** {datetime.now().strftime('%I:%M %p')}")

# ---------------- APPLY FILTERS ----------------
try:
    if submitted or st.session_state.filtered_data is None:
        filtered = df[
            (df["Order Date"].dt.date >= date_range[0]) &
            (df["Order Date"].dt.date <= date_range[1]) &
            (df["Status"].isin(status_filter)) &
            (df["Payment Type"].isin(payment_filter))
        ].copy()

        if tier_filter and "City Tier" in filtered.columns:
            filtered = filtered[filtered["City Tier"].isin(tier_filter)]

        if len(filtered) == 0:
            st.warning("⚠️ No data matches filters")
            st.stop()
        
        st.session_state.filtered_data = filtered
        st.session_state.filters_applied = True
    else:
        filtered = st.session_state.filtered_data

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.stop()

# ---------------- KEY METRICS (Cleaned up - removed 3 cards) ----------------
st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

total_orders = filtered["Order Number"].nunique()
total_revenue = filtered["Grand Total"].sum()
avg_order_value = filtered["Grand Total"].mean() if len(filtered) > 0 else 0

with col1:
    st.markdown(create_metric_card("Total Orders", f"{total_orders:,}"), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card("Total Revenue", f"₹{total_revenue:,.0f}"), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card("Avg Order Value", f"₹{avg_order_value:,.0f}"), unsafe_allow_html=True)

# Second row with payment metrics
col1, col2, col3 = st.columns(3)

prepaid_orders = filtered[filtered["Payment Type"] == "Prepaid"].shape[0]
cod_orders = filtered[filtered["Payment Type"] == "COD"].shape[0]
confirmed_orders = filtered[filtered["Status"].str.contains("Confirmed|Delivered|Shipped", case=False, na=False)].shape[0]
total_transactions = len(filtered)
payment_success_ratio = (confirmed_orders / total_transactions * 100) if total_transactions > 0 else 0

with col1:
    st.markdown(create_metric_card("Prepaid Orders", f"{prepaid_orders:,}", 
                                    f"{(prepaid_orders/total_transactions*100):.1f}%"), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card("COD Orders", f"{cod_orders:,}", 
                                    f"{(cod_orders/total_transactions*100):.1f}%"), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card("Success Rate", f"{payment_success_ratio:.1f}%", 
                                    f"{confirmed_orders:,} confirmed"), unsafe_allow_html=True)

# Optional: Show discount metric only if relevant
if "Total Discount" in filtered.columns:
    total_discount = filtered["Total Discount"].sum()
    if total_discount > 0:
        st.markdown(create_metric_card("Total Discounts", f"₹{total_discount:,.0f}"), unsafe_allow_html=True)

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", 
    "🎯 Marketing", 
    "💰 Discounts & RTO", 
    "🕐 Time Patterns",
    "📦 Products",
    "👥 Customers"
])

# ============ TAB 1: OVERVIEW ============
with tab1:
    st.markdown('<div class="section-header">📊 Revenue & Orders Trend</div>', unsafe_allow_html=True)
    
    try:
        if time_grain == "Daily":
            trend_data = filtered.groupby(filtered["Order Date"].dt.date).agg({
                "Grand Total": "sum",
                "Order Number": "count"
            }).reset_index()
            trend_data.columns = ["Date", "Revenue", "Orders"]
            title_text = "Daily Performance"
        elif time_grain == "Weekly":
            filtered_copy = filtered.copy()
            filtered_copy["Week"] = filtered_copy["Order Date"].dt.to_period('W').dt.start_time
            trend_data = filtered_copy.groupby("Week").agg({
                "Grand Total": "sum",
                "Order Number": "count"
            }).reset_index()
            trend_data.columns = ["Date", "Revenue", "Orders"]
            title_text = "Weekly Performance"
        else:
            filtered_copy = filtered.copy()
            filtered_copy["Month"] = filtered_copy["Order Date"].dt.to_period('M').dt.start_time
            trend_data = filtered_copy.groupby("Month").agg({
                "Grand Total": "sum",
                "Order Number": "count"
            }).reset_index()
            trend_data.columns = ["Date", "Revenue", "Orders"]
            title_text = "Monthly Performance"
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=trend_data["Date"], 
                y=trend_data["Revenue"],
                name="Revenue",
                marker=dict(
                    color=trend_data["Revenue"],
                    colorscale='Blues',
                    showscale=False,
                    line=dict(width=0)
                ),
                hovertemplate='%{y:,.0f}<extra></extra>'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=trend_data["Date"], 
                y=trend_data["Orders"],
                name="Orders",
                mode='lines+markers',
                line=dict(color='#f093fb', width=3),
                marker=dict(size=8, color='#f093fb'),
                hovertemplate='%{y}<extra></extra>'
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title=dict(
                text=title_text, 
                font=dict(size=18, color='#1e293b', family="Arial, sans-serif", weight=600),
                x=0.02
            ),
            height=450,
            hovermode='x unified',
            plot_bgcolor='#fafbfc',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=13, color='#64748b'),
            margin=dict(l=70, r=70, t=70, b=60),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#e2e8f0",
                borderwidth=1
            )
        )
        
        fig.update_xaxes(
            showgrid=False, 
            showline=True, 
            linewidth=1, 
            linecolor='#e2e8f0',
            tickfont=dict(color='#64748b', size=12)
        )
        fig.update_yaxes(
            showgrid=True, 
            gridcolor='#f1f5f9', 
            gridwidth=1,
            secondary_y=False,
            tickfont=dict(color='#64748b', size=12),
            title=dict(text="Revenue (₹)", font=dict(size=13, color='#475569'))
        )
        fig.update_yaxes(
            showgrid=False, 
            secondary_y=True,
            tickfont=dict(color='#64748b', size=12),
            title=dict(text="Orders", font=dict(size=13, color='#475569'))
        )
        
        st.plotly_chart(fig, use_container_width=True, config={
            'responsive': True, 
            'displayModeBar': False,
            'doubleClick': 'reset'
        })
    except Exception as e:
        st.error(f"Error rendering chart: {str(e)}")
    
    # Payment Split & Geographic in 2 columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">💳 Payment Distribution</div>', unsafe_allow_html=True)
        
        try:
            payment_split = filtered.groupby("Payment Type").agg({
                "Order Number": "count",
                "Grand Total": "sum"
            }).reset_index()
            payment_split.columns = ["Type", "Orders", "Revenue"]
            
            fig = go.Figure(data=[go.Pie(
                labels=payment_split["Type"],
                values=payment_split["Orders"],
                hole=0.6,
                marker=dict(
                    colors=['#667eea', '#f093fb'],
                    line=dict(color='white', width=3)
                ),
                textinfo='label+percent',
                textfont_size=14,
                textfont_color='white',
                textposition='inside',
                hovertemplate='<b>%{label}</b><br>Orders: %{value:,}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                height=380,
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=13, color='#64748b'),
                margin=dict(l=20, r=20, t=30, b=20),
                showlegend=False,
                annotations=[dict(
                    text=f'<b>{total_orders:,}</b><br><span style="font-size:12px">Total Orders</span>',
                    x=0.5, y=0.5,
                    font_size=16,
                    showarrow=False,
                    font=dict(color='#1e293b')
                )]
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown('<div class="section-header">🗺️ Top States</div>', unsafe_allow_html=True)
        
        if "Billing State" in filtered.columns:
            try:
                state_data = filtered.groupby("Billing State").agg({
                    "Order Number": "count",
                    "Grand Total": "sum"
                }).reset_index().sort_values("Grand Total", ascending=True).tail(8)
                state_data.columns = ["State", "Orders", "Revenue"]
                
                fig = go.Figure(data=[go.Bar(
                    x=state_data["Revenue"],
                    y=state_data["State"],
                    orientation='h',
                    marker=dict(
                        color=state_data["Revenue"],
                        colorscale='Teal',
                        showscale=False,
                        line=dict(width=0)
                    ),
                    text=state_data["Orders"],
                    texttemplate='%{text} orders',
                    textposition='outside',
                    textfont=dict(size=11, color='#64748b'),
                    hovertemplate='<b>%{y}</b><br>Revenue: ₹%{x:,.0f}<br>Orders: %{text}<extra></extra>'
                )])
                
                fig.update_layout(
                    height=380,
                    xaxis_title="Revenue (₹)",
                    plot_bgcolor='#fafbfc',
                    paper_bgcolor='white',
                    font=dict(family="Arial, sans-serif", size=12, color='#64748b'),
                    margin=dict(l=100, r=60, t=30, b=50),
                    xaxis=dict(showgrid=True, gridcolor='#f1f5f9', showline=False),
                    yaxis=dict(showgrid=False, showline=False, tickfont=dict(size=12))
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # City Tier Analysis
    if "City Tier" in filtered.columns:
        st.markdown('<div class="section-header">🏙️ City Tier Performance</div>', unsafe_allow_html=True)
        
        try:
            tier_data = filtered.groupby("City Tier").agg({
                "Order Number": "count",
                "Grand Total": "sum"
            }).reset_index()
            tier_data.columns = ["Tier", "Orders", "Revenue"]
            tier_data["AOV"] = tier_data["Revenue"] / tier_data["Orders"]
            
            tier_order = ["Tier 1", "Tier 2", "Tier 3"]
            tier_data["Tier"] = pd.Categorical(tier_data["Tier"], categories=tier_order, ordered=True)
            tier_data = tier_data.sort_values("Tier")
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=tier_data["Tier"],
                y=tier_data["Orders"],
                name="Orders",
                marker=dict(
                    color=['#667eea', '#764ba2', '#f093fb'],
                    line=dict(width=0)
                ),
                text=tier_data["Orders"],
                textposition='outside',
                textfont=dict(size=12, color='#64748b'),
                hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=tier_data["Tier"],
                y=tier_data["AOV"],
                name="AOV",
                mode='lines+markers+text',
                yaxis='y2',
                line=dict(color='#10b981', width=3),
                marker=dict(size=12, color='#10b981', symbol='diamond'),
                text=tier_data["AOV"].apply(lambda x: f'₹{x:,.0f}'),
                textposition='top center',
                textfont=dict(size=11, color='#10b981'),
                hovertemplate='<b>%{x}</b><br>AOV: ₹%{y:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                height=400,
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=13, color='#64748b'),
                margin=dict(l=60, r=60, t=40, b=60),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#e2e8f0",
                    borderwidth=1
                ),
                xaxis=dict(
                    showgrid=False, 
                    showline=True, 
                    linewidth=1, 
                    linecolor='#e2e8f0',
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title="Orders",
                    showgrid=True,
                    gridcolor='#f1f5f9',
                    tickfont=dict(size=12),
                    title_font=dict(size=13, color='#475569')
                ),
                yaxis2=dict(
                    title="AOV (₹)",
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    tickfont=dict(size=12),
                    title_font=dict(size=13, color='#475569')
                )
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============ TAB 2: MARKETING ============
with tab2:
    st.markdown('<div class="section-header">🎯 Marketing Attribution</div>', unsafe_allow_html=True)
    
    if "Utm Source" in filtered.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            utm_data = filtered.groupby("Utm Source").agg({
                "Order Number": "count",
                "Grand Total": "sum"
            }).reset_index()
            utm_data.columns = ["Source", "Orders", "Revenue"]
            utm_data["AOV"] = utm_data["Revenue"] / utm_data["Orders"]
            utm_data = utm_data.sort_values("Revenue", ascending=False)
            
            fig = px.bar(
                utm_data, 
                x="Source", 
                y="Revenue",
                color="Revenue",
                color_continuous_scale="Viridis",
                text="Orders",
                title="Revenue by UTM Source"
            )
            
            fig.update_traces(
                texttemplate='%{text} orders',
                textposition='outside',
                textfont=dict(size=11, color='#64748b')
            )
            
            fig.update_layout(
                height=400,
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#64748b'),
                margin=dict(l=60, r=60, t=70, b=60),
                xaxis=dict(showgrid=False, showline=True, linecolor='#e2e8f0'),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        
        with col2:
            fig = px.bar(
                utm_data, 
                x="Source", 
                y="AOV",
                color="AOV",
                color_continuous_scale="Teal",
                text="AOV",
                title="AOV by UTM Source"
            )
            
            fig.update_traces(
                texttemplate='₹%{text:,.0f}',
                textposition='outside',
                textfont=dict(size=11, color='#64748b')
            )
            
            fig.update_layout(
                height=400,
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#64748b'),
                margin=dict(l=60, r=60, t=70, b=60),
                xaxis=dict(showgrid=False, showline=True, linecolor='#e2e8f0'),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
    
    if "Utm Campaign" in filtered.columns:
        st.markdown("### 📣 Campaign Performance")
        
        campaign_data = filtered.groupby("Utm Campaign").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        campaign_data.columns = ["Campaign", "Orders", "Revenue"]
        campaign_data["AOV"] = campaign_data["Revenue"] / campaign_data["Orders"]
        campaign_data = campaign_data.sort_values("Revenue", ascending=False).head(10)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Orders',
            x=campaign_data["Campaign"],
            y=campaign_data["Orders"],
            marker_color='#667eea',
            text=campaign_data["Orders"],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            name='Revenue/100',
            x=campaign_data["Campaign"],
            y=campaign_data["Revenue"]/100,
            marker_color='#f093fb',
            text=campaign_data["Revenue"].apply(lambda x: f'₹{x/1000:.1f}K'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Top 10 Campaigns",
            barmode='group',
            height=450,
            plot_bgcolor='#fafbfc',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color='#64748b'),
            margin=dict(l=60, r=60, t=70, b=100),
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='#e2e8f0',
                tickangle=-45,
                tickfont=dict(size=11)
            ),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
            title=dict(x=0.02, font=dict(size=16, color='#1e293b')),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})

# ============ TAB 3: DISCOUNTS & RTO ============
with tab3:
    st.markdown('<div class="section-header">💰 Discount Analysis</div>', unsafe_allow_html=True)
    
    if "Total Discount" in filtered.columns:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_disc = filtered["Total Discount"].sum()
            st.markdown(create_metric_card("Total Discounts", f"₹{total_disc:,.0f}"), unsafe_allow_html=True)
        
        with col2:
            orders_with_disc = filtered[filtered["Total Discount"] > 0].shape[0]
            disc_penetration = (orders_with_disc / len(filtered) * 100) if len(filtered) > 0 else 0
            st.markdown(create_metric_card("Discount Penetration", f"{disc_penetration:.1f}%", 
                                          f"{orders_with_disc:,} orders"), unsafe_allow_html=True)
        
        with col3:
            avg_disc = filtered[filtered["Total Discount"] > 0]["Total Discount"].mean()
            st.markdown(create_metric_card("Avg Discount", f"₹{avg_disc:,.0f}"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            disc_comparison = filtered.copy()
            disc_comparison["Has_Discount"] = disc_comparison["Total Discount"] > 0
            disc_comp = disc_comparison.groupby("Has_Discount").agg({
                "Order Number": "count",
                "Grand Total": "sum"
            }).reset_index()
            disc_comp["Has_Discount"] = disc_comp["Has_Discount"].map({True: "With Discount", False: "No Discount"})
            disc_comp.columns = ["Category", "Orders", "Revenue"]
            
            fig = px.pie(
                disc_comp, 
                values="Orders", 
                names="Category",
                title="Orders: Discount vs No Discount",
                color_discrete_sequence=['#667eea', '#f093fb'],
                hole=0.5
            )
            
            fig.update_traces(
                textinfo='label+percent',
                textfont_size=13,
                marker=dict(line=dict(color='white', width=2))
            )
            
            fig.update_layout(
                height=380,
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=60, b=20),
                font=dict(family="Arial, sans-serif", size=12),
                title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        
        with col2:
            aov_comp = disc_comparison.groupby("Has_Discount").agg({
                "Grand Total": "mean"
            }).reset_index()
            aov_comp["Has_Discount"] = aov_comp["Has_Discount"].map({True: "With Discount", False: "No Discount"})
            aov_comp.columns = ["Category", "AOV"]
            
            fig = px.bar(
                aov_comp, 
                x="Category", 
                y="AOV",
                title="AOV Comparison",
                color="AOV",
                color_continuous_scale="Mint",
                text="AOV"
            )
            
            fig.update_traces(
                texttemplate='₹%{text:,.0f}',
                textposition='outside',
                textfont=dict(size=13, color='#64748b')
            )
            
            fig.update_layout(
                height=380,
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                margin=dict(l=60, r=60, t=60, b=60),
                font=dict(family="Arial, sans-serif", size=12),
                xaxis=dict(showgrid=False, showline=True, linecolor='#e2e8f0'),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
    
    # RTO Risk
    st.markdown('<div class="section-header">📦 RTO Risk Analysis</div>', unsafe_allow_html=True)
    
    if "RTO Risk" in filtered.columns and "RTO Score" in filtered.columns:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            high_rto = filtered[filtered["RTO Risk"].str.contains("high", case=False, na=False)].shape[0]
            rto_pct = (high_rto / len(filtered) * 100) if len(filtered) > 0 else 0
            st.markdown(create_metric_card("High RTO Risk", f"{high_rto:,}", 
                                          f"{rto_pct:.1f}%"), unsafe_allow_html=True)
        
        with col2:
            avg_rto_score = filtered["RTO Score"].mean()
            st.markdown(create_metric_card("Avg RTO Score", f"{avg_rto_score:.2f}"), unsafe_allow_html=True)
        
        with col3:
            cod_rto = filtered[(filtered["Payment Type"] == "COD") & 
                              (filtered["RTO Risk"].str.contains("high", case=False, na=False))].shape[0]
            st.markdown(create_metric_card("High RTO COD", f"{cod_rto:,}"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            rto_dist = filtered.groupby("RTO Risk")["Order Number"].count().reset_index()
            rto_dist.columns = ["Risk Level", "Orders"]
            
            fig = px.bar(
                rto_dist, 
                x="Risk Level", 
                y="Orders",
                title="RTO Risk Distribution",
                color="Orders",
                color_continuous_scale="Reds",
                text="Orders"
            )
            
            fig.update_traces(textposition='outside', textfont=dict(size=12))
            fig.update_layout(
                height=380,
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                margin=dict(l=60, r=60, t=60, b=60),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        
        with col2:
            rto_payment = filtered.groupby(["Payment Type", "RTO Risk"]).size().reset_index(name='Orders')
            
            fig = px.bar(
                rto_payment, 
                x="Payment Type", 
                y="Orders", 
                color="RTO Risk",
                title="RTO by Payment Type",
                barmode='group',
                color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444']
            )
            
            fig.update_layout(
                height=380,
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                margin=dict(l=60, r=60, t=60, b=60),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})

# ============ TAB 4: TIME PATTERNS ============
with tab4:
    st.markdown('<div class="section-header">🕐 Time-Based Patterns</div>', unsafe_allow_html=True)
    
    if "Order Hour" in filtered.columns:
        hourly = filtered.groupby("Order Hour").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        hourly.columns = ["Hour", "Orders", "Revenue"]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hourly["Hour"],
            y=hourly["Orders"],
            mode='lines+markers',
            name='Orders',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea'),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)',
            hovertemplate='<b>Hour %{x}:00</b><br>Orders: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Orders by Hour of Day",
            xaxis_title="Hour (24-hour format)",
            yaxis_title="Orders",
            height=420,
            plot_bgcolor='#fafbfc',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color='#64748b'),
            margin=dict(l=60, r=60, t=70, b=60),
            hovermode='x unified',
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='#e2e8f0',
                tickmode='linear',
                tick0=0,
                dtick=2
            ),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
            title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        
        # Peak Hours Table
        peak_hours = hourly.nlargest(5, "Orders")[["Hour", "Orders", "Revenue"]]
        peak_hours["Revenue"] = peak_hours["Revenue"].apply(lambda x: f"₹{x:,.0f}")
        
        st.markdown("### 🔥 Top 5 Peak Hours")
        st.dataframe(
            peak_hours,
            use_container_width=True,
            column_config={
                "Hour": st.column_config.NumberColumn("Hour", format="%d:00"),
                "Orders": st.column_config.NumberColumn("Orders", format="%d"),
                "Revenue": st.column_config.TextColumn("Revenue")
            }
        )
    
    if "Order Day" in filtered.columns:
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_data = filtered.groupby("Order Day").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        day_data.columns = ["Day", "Orders", "Revenue"]
        day_data["Day"] = pd.Categorical(day_data["Day"], categories=day_order, ordered=True)
        day_data = day_data.sort_values("Day")
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=day_data["Day"],
                y=day_data["Orders"],
                name="Orders",
                marker=dict(
                    color=day_data["Orders"],
                    colorscale='Blues',
                    showscale=False
                ),
                hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=day_data["Day"],
                y=day_data["Revenue"],
                name="Revenue",
                mode='lines+markers',
                line=dict(color='#f093fb', width=3),
                marker=dict(size=10, color='#f093fb'),
                hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Performance by Day of Week",
            height=420,
            plot_bgcolor='#fafbfc',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color='#64748b'),
            margin=dict(l=60, r=60, t=70, b=60),
            hovermode='x unified',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False, showline=True, linecolor='#e2e8f0'),
            title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
        )
        
        fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9', secondary_y=False, title="Orders")
        fig.update_yaxes(showgrid=False, secondary_y=True, title="Revenue (₹)")
        
        st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})

# ============ TAB 5: PRODUCTS ============
with tab5:
    st.markdown('<div class="section-header">📦 Product Performance</div>', unsafe_allow_html=True)
    
    if "Product Name" in filtered.columns:
        product_data = filtered.groupby("Product Name").agg({
            "Order Number": "count",
            "Grand Total": "sum",
            "Total Qty Ordered": "sum"
        }).reset_index()
        product_data.columns = ["Product", "Orders", "Revenue", "Quantity"]
        product_data["AOV"] = product_data["Revenue"] / product_data["Orders"]
        product_data = product_data.sort_values("Revenue", ascending=False)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            top_product = product_data.iloc[0]["Product"] if len(product_data) > 0 else "N/A"
            top_revenue = product_data.iloc[0]["Revenue"] if len(product_data) > 0 else 0
            st.markdown(create_metric_card("Top Product", top_product[:20], 
                                          f"₹{top_revenue:,.0f}"), unsafe_allow_html=True)
        
        with col2:
            total_products = filtered["Product Name"].nunique()
            st.markdown(create_metric_card("Total Products", f"{total_products}"), unsafe_allow_html=True)
        
        with col3:
            avg_qty = filtered["Total Qty Ordered"].mean() if "Total Qty Ordered" in filtered.columns else 0
            st.markdown(create_metric_card("Avg Qty/Order", f"{avg_qty:.1f}"), unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            top_products = product_data.head(10)
            
            fig = px.bar(
                top_products, 
                x="Revenue", 
                y="Product",
                title="Top 10 Products by Revenue",
                orientation='h',
                color="Revenue",
                color_continuous_scale="Blues",
                text="Orders"
            )
            
            fig.update_traces(
                texttemplate='%{text} orders',
                textposition='outside',
                textfont=dict(size=11, color='#64748b')
            )
            
            fig.update_layout(
                height=480,
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#64748b'),
                margin=dict(l=150, r=60, t=70, b=60),
                xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Revenue (₹)"),
                yaxis=dict(showgrid=False, title=""),
                title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        
        with col2:
            fig = px.scatter(
                product_data, 
                x="Orders", 
                y="AOV", 
                size="Revenue",
                hover_data=["Product"],
                title="Orders vs AOV (size = Revenue)",
                color="Revenue",
                color_continuous_scale="Viridis"
            )
            
            fig.update_layout(
                height=480,
                plot_bgcolor='#fafbfc',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#64748b'),
                margin=dict(l=60, r=60, t=70, b=60),
                xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Orders"),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="AOV (₹)"),
                title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        
        # Product Table
        st.markdown("### 📊 Detailed Product Metrics")
        
        product_display = product_data.head(15).copy()
        product_display["Revenue"] = product_display["Revenue"].apply(lambda x: f"₹{x:,.0f}")
        product_display["AOV"] = product_display["AOV"].apply(lambda x: f"₹{x:,.0f}")
        
        st.dataframe(
            product_display,
            use_container_width=True,
            column_config={
                "Product": st.column_config.TextColumn("Product", width="large"),
                "Orders": st.column_config.NumberColumn("Orders", format="%d"),
                "Revenue": st.column_config.TextColumn("Revenue"),
                "Quantity": st.column_config.NumberColumn("Qty Sold", format="%d"),
                "AOV": st.column_config.TextColumn("AOV")
            }
        )

# ============ TAB 6: CUSTOMERS (RFM) ============
with tab6:
    st.markdown('<div class="section-header">👥 RFM Customer Segmentation</div>', unsafe_allow_html=True)
    
    if "Customer Phone" in filtered.columns:
        try:
            rfm_data = filtered[["Customer Phone", "Customer Name", "Order Date", "Grand Total"]].copy()
            rfm_data.columns = ["Phone", "Name", "OrderDate", "Revenue"]
            rfm_data = rfm_data.dropna(subset=["Phone", "OrderDate", "Revenue"])
            
            if len(rfm_data) == 0:
                st.warning("⚠️ No customer data available")
            else:
                rfm_data["CustomerID"] = rfm_data["Phone"].apply(
                    lambda x: hashlib.md5(str(x).encode()).hexdigest()[:8]
                )
                
                rfm_data["HashedName"] = rfm_data["Name"].apply(
                    lambda x: hashlib.md5(str(x).encode()).hexdigest()[:8] if pd.notna(x) else "Unknown"
                )
                
                analysis_date = filtered["Order Date"].max()
                
                rfm = rfm_data.groupby("CustomerID").agg({
                    "OrderDate": lambda x: (analysis_date - x.max()).days,
                    "Phone": "count",
                    "Revenue": "sum",
                    "HashedName": "first"
                }).reset_index()
                
                rfm.columns = ["CustomerID", "Recency", "Frequency", "Monetary", "HashedName"]
                
                rfm["R_Score"] = rfm_score(rfm["Recency"], n_bins=5, reverse=True)
                rfm["F_Score"] = rfm_score(rfm["Frequency"], n_bins=5, reverse=False)
                rfm["M_Score"] = rfm_score(rfm["Monetary"], n_bins=5, reverse=False)
                
                rfm["R_Score"] = rfm["R_Score"].astype(str)
                rfm["F_Score"] = rfm["F_Score"].astype(str)
                rfm["M_Score"] = rfm["M_Score"].astype(str)
                
                def segment_customer(row):
                    try:
                        r_score = int(row["R_Score"]) if str(row["R_Score"]).isdigit() else 3
                        f_score = int(row["F_Score"]) if str(row["F_Score"]).isdigit() else 3
                        m_score = int(row["M_Score"]) if str(row["M_Score"]).isdigit() else 3
                        score = r_score + f_score + m_score
                        
                        if score >= 13:
                            return "Champions"
                        elif score >= 11:
                            return "Loyal"
                        elif score >= 9:
                            return "Potential"
                        elif score >= 7:
                            return "At Risk"
                        else:
                            return "Lost"
                    except:
                        return "Unknown"
                
                rfm["Segment"] = rfm.apply(segment_customer, axis=1)
                
                segment_summary = rfm.groupby("Segment").agg({
                    "CustomerID": "count",
                    "Monetary": "sum"
                }).reset_index()
                segment_summary.columns = ["Segment", "Customers", "Total Revenue"]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        segment_summary, 
                        values="Customers", 
                        names="Segment",
                        title="Customer Segmentation",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                        hole=0.5
                    )
                    
                    fig.update_traces(
                        textinfo='label+percent',
                        textfont_size=13,
                        marker=dict(line=dict(color='white', width=2))
                    )
                    
                    fig.update_layout(
                        height=400,
                        paper_bgcolor='white',
                        margin=dict(l=20, r=20, t=60, b=20),
                        title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
                
                with col2:
                    fig = px.bar(
                        segment_summary, 
                        x="Segment", 
                        y="Total Revenue",
                        title="Revenue by Segment",
                        color="Total Revenue",
                        color_continuous_scale="Viridis",
                        text="Total Revenue"
                    )
                    
                    fig.update_traces(
                        texttemplate='₹%{text:,.0f}',
                        textposition='outside',
                        textfont=dict(size=11, color='#64748b')
                    )
                    
                    fig.update_layout(
                        height=400,
                        plot_bgcolor='#fafbfc',
                        paper_bgcolor='white',
                        margin=dict(l=60, r=60, t=60, b=60),
                        xaxis=dict(showgrid=False, showline=True, linecolor='#e2e8f0'),
                        yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                        title=dict(x=0.02, font=dict(size=16, color='#1e293b'))
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
                
                st.markdown("### 🌟 Top 15 Customers by Revenue")
                
                top_customers = rfm.nlargest(15, "Monetary")[["HashedName", "Recency", "Frequency", "Monetary", "Segment"]].copy()
                top_customers.columns = ["Customer ID", "Days Since Last Order", "Total Orders", "Total Spent", "Segment"]
                top_customers = top_customers.reset_index(drop=True)
                top_customers.index = top_customers.index + 1
                top_customers["Days Since Last Order"] = top_customers["Days Since Last Order"].astype(int)
                top_customers["Total Orders"] = top_customers["Total Orders"].astype(int)
                top_customers["Total Spent"] = top_customers["Total Spent"].apply(lambda x: f"₹{x:,.0f}")
                
                st.dataframe(
                    top_customers,
                    use_container_width=True,
                    column_config={
                        "Customer ID": st.column_config.TextColumn("Customer ID", width="medium"),
                        "Days Since Last Order": st.column_config.NumberColumn("Days Ago", format="%d"),
                        "Total Orders": st.column_config.NumberColumn("Orders", format="%d"),
                        "Total Spent": st.column_config.TextColumn("Revenue"),
                        "Segment": st.column_config.TextColumn("Segment", width="small")
                    }
                )
                
                # RFM Distribution Charts
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fig = px.histogram(
                        rfm, 
                        x="Recency", 
                        nbins=30,
                        title="Recency Distribution",
                        color_discrete_sequence=["#667eea"]
                    )
                    
                    fig.update_layout(
                        height=300,
                        plot_bgcolor='#fafbfc',
                        paper_bgcolor='white',
                        margin=dict(l=50, r=50, t=50, b=50),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                        title=dict(x=0.05, font=dict(size=14, color='#1e293b'))
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
                
                with col2:
                    fig = px.histogram(
                        rfm, 
                        x="Frequency", 
                        nbins=20,
                        title="Frequency Distribution",
                        color_discrete_sequence=["#10b981"]
                    )
                    
                    fig.update_layout(
                        height=300,
                        plot_bgcolor='#fafbfc',
                        paper_bgcolor='white',
                        margin=dict(l=50, r=50, t=50, b=50),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                        title=dict(x=0.05, font=dict(size=14, color='#1e293b'))
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
                
                with col3:
                    fig = px.histogram(
                        rfm, 
                        x="Monetary", 
                        nbins=30,
                        title="Monetary Distribution",
                        color_discrete_sequence=["#f59e0b"]
                    )
                    
                    fig.update_layout(
                        height=300,
                        plot_bgcolor='#fafbfc',
                        paper_bgcolor='white',
                        margin=dict(l=50, r=50, t=50, b=50),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                        title=dict(x=0.05, font=dict(size=14, color='#1e293b'))
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
                    
        except Exception as e:
            st.error(f"❌ Error in RFM analysis: {str(e)}")
            st.info("💡 Insufficient customer data for analysis")

