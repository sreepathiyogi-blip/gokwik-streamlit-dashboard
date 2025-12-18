import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import date, datetime
import hashlib

# ------------ CONFIG ------------
st.set_page_config(
    page_title="GoKwik Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------ CUSTOM CSS ------------
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
    }
    
    /* Ensure consistent sizing */
    .block-container {
        max-width: 100%;
        padding: 1rem 2rem;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 10px 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }
    
    /* Metric value */
    .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: #667eea;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric label */
    .metric-label {
        font-size: 13px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    /* Section headers */
    .section-header {
        font-size: 24px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 40px 0 25px 0;
        padding: 20px 25px;
        border-left: 6px solid #667eea;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chart containers */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        background: white;
        margin: 10px 0;
    }
    
    /* Remove streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* File uploader styling */
    .uploadedFile {
        background: white;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Streamlit elements */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        width: 100%;
        height: 80px;
        font-size: 13px;
        white-space: pre-line;
        line-height: 1.4;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton>button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.5);
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .metric-card {
            padding: 15px;
            min-height: 120px;
        }
        
        .metric-value {
            font-size: 28px;
        }
        
        .section-header {
            font-size: 18px;
            padding: 12px 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
DATA_FILE = f"{DATA_DIR}/latest.parquet"
os.makedirs(DATA_DIR, exist_ok=True)

# ------------ HELPERS ------------
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

def hash_customer_name(name):
    """Hash customer name for privacy"""
    if pd.isna(name):
        return "Unknown"
    return hashlib.md5(str(name).encode()).hexdigest()[:8]

def create_metric_card(label, value, delta=None, delta_color="normal"):
    delta_html = f'<div style="color: {"#10b981" if delta_color == "normal" else "#ef4444"}; font-size: 14px; font-weight: 600; margin-top: 8px;">{delta}</div>' if delta else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def get_city_tier(pincode):
    """Classify cities into tiers based on pincode"""
    if pd.isna(pincode):
        return 'Unknown'
    
    pincode_str = str(pincode).strip()
    if len(pincode_str) < 3:
        return 'Unknown'
    
    pincode_prefix = pincode_str[:3]
    
    try:
        pincode_num = int(pincode_prefix)
    except:
        return 'Unknown'
    
    # Tier 1 cities (Major metros)
    tier_1 = {
        400, 401,
        110, 121, 122, 201, 124, 125, 127, 128,
        560, 562, 563,
        500, 501, 502, 503, 504, 505, 508,
        600, 601, 602, 603,
        700, 711, 712, 713, 721, 722, 743,
        411, 412,
        380, 382, 383,
    }
    
    # Tier 2 cities
    tier_2 = {
        302, 303,
        226, 227,
        208, 209,
        440, 441, 442,
        452, 453,
        462, 463,
        530, 531,
        390, 391,
        141, 142,
        282, 283,
        422, 423,
        250, 251,
        360, 361,
        221, 222,
        190, 191, 192, 193, 194,
        143,
        211, 212,
        834, 835,
        641, 642,
        520, 521,
        342, 344,
        625, 626,
        492, 493,
        324, 325,
        781, 782, 783,
        160, 140,
    }
    
    if pincode_num in tier_1:
        return 'Tier 1'
    elif pincode_num in tier_2:
        return 'Tier 2'
    else:
        return 'Tier 3'

def map_utm_source(utm_source):
    """Map UTM SOURCE to platform - UPDATED TO USE UTM_SOURCE (fb, ig = Meta, google = Google)"""
    if pd.isna(utm_source):
        return 'Other'
    
    utm_lower = str(utm_source).lower().strip()
    
    # Meta platforms
    if any(x in utm_lower for x in ['facebook', 'fb']):
        return 'Meta'
    elif any(x in utm_lower for x in ['instagram', 'ig']):
        return 'Meta'
    # Google
    elif 'google' in utm_lower:
        return 'Google'
    # Organic/Direct
    elif any(x in utm_lower for x in ['organic', 'direct']):
        return 'Organic'
    else:
        return 'Other'

# State coordinates mapping
STATE_COORDS = {
    'ANDHRA PRADESH': (15.9129, 79.7400),
    'ARUNACHAL PRADESH': (28.2180, 94.7278),
    'ASSAM': (26.2006, 92.9376),
    'BIHAR': (25.0961, 85.3131),
    'CHHATTISGARH': (21.2787, 81.8661),
    'GOA': (15.2993, 74.1240),
    'GUJARAT': (22.2587, 71.1924),
    'HARYANA': (29.0588, 76.0856),
    'HIMACHAL PRADESH': (31.1048, 77.1734),
    'JHARKHAND': (23.6102, 85.2799),
    'KARNATAKA': (15.3173, 75.7139),
    'KERALA': (10.8505, 76.2711),
    'MADHYA PRADESH': (22.9734, 78.6569),
    'MAHARASHTRA': (19.7515, 75.7139),
    'MANIPUR': (24.6637, 93.9063),
    'MEGHALAYA': (25.4670, 91.3662),
    'MIZORAM': (23.1645, 92.9376),
    'NAGALAND': (26.1584, 94.5624),
    'ODISHA': (20.9517, 85.0985),
    'PUNJAB': (31.1471, 75.3412),
    'RAJASTHAN': (27.0238, 74.2179),
    'SIKKIM': (27.5330, 88.5122),
    'TAMIL NADU': (11.1271, 78.6569),
    'TELANGANA': (18.1124, 79.0193),
    'TRIPURA': (23.9408, 91.9882),
    'UTTAR PRADESH': (26.8467, 80.9462),
    'UTTARAKHAND': (30.0668, 79.0193),
    'WEST BENGAL': (22.9868, 87.8550),
    'DELHI': (28.7041, 77.1025),
    'JAMMU AND KASHMIR': (33.7782, 76.5762),
    'LADAKH': (34.1526, 77.5771),
    'PUDUCHERRY': (11.9416, 79.8083),
    'CHANDIGARH': (30.7333, 76.7794),
    'ANDAMAN AND NICOBAR ISLANDS': (11.7401, 92.6586),
    'DADRA AND NAGAR HAVELI AND DAMAN AND DIU': (20.1809, 73.0169),
    'LAKSHADWEEP': (10.5667, 72.6417),
}

# ------------ HEADER ------------
st.markdown("""
<div class="dashboard-header">
    <h1>📊 GoKwik Order Analytics Dashboard</h1>
    <p>Real-time insights into your e-commerce performance</p>
</div>
""", unsafe_allow_html=True)

# ------------ SIDEBAR FILE UPLOAD ------------
with st.sidebar:
    st.markdown("### 📁 Data Upload")
    uploaded_file = st.file_uploader(
        "Upload Order Report",
        type=["csv", "xlsx"],
        help="Upload CSV or Excel file with order data"
    )
    
    st.markdown("---")
    
    if uploaded_file:
        st.success("✅ File uploaded successfully")

# ------------ UPLOAD PROCESSING ------------
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
        st.error(f"❌ Missing columns: {', '.join(missing)}")
        st.stop()

    # Data cleaning
    df["Order Date"] = pd.to_datetime(df["Created At"], errors="coerce", dayfirst=True)
    df = df[df["Order Date"].notna()]
    
    df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors="coerce")
    df["Status"] = df["Merchant Order Status"]
    df["Payment Method"] = df["Payment Method"].astype(str).str.upper()
    df["Payment Type"] = df["Payment Method"].apply(
        lambda x: "COD" if "COD" in str(x) else "Prepaid"
    )
    
    # Customer ID
    if "Customer Phone" in df.columns:
        df["Customer ID"] = df["Customer Phone"].apply(lambda x: str(x).split('|')[0] if pd.notna(x) else "Unknown")
    elif "Customer Name" in df.columns:
        df["Customer ID"] = df["Customer Name"].apply(hash_customer_name)
    
    # City tier by pincode
    if "Billing Pincode" in df.columns:
        df["City Tier"] = df["Billing Pincode"].apply(get_city_tier)
    else:
        df["City Tier"] = "Unknown"
    
    # Map UTM source to platforms (UPDATED - NOW USING utm_source)
    if "Utm Source" in df.columns:
        df["UTM Platform"] = df["Utm Source"].apply(map_utm_source)
    else:
        df["UTM Platform"] = "Other"

    save_data(df)

# ------------ LOAD DATA ------------
if not uploaded_file:
    df = load_data()
    if df is None:
        st.info("👆 Please upload a file to view the dashboard")
        st.stop()

if "Order Date" not in df.columns:
    st.error("⚠️ Data corrupted. Please re-upload the file.")
    st.stop()

# ------------ QUICK FILTERS (TOP BUTTONS) - SORTED BY ORDERS ------------
if "UTM Platform" in df.columns:
    st.markdown('<div class="section-header">🎯 Quick Platform Filters</div>', unsafe_allow_html=True)
    
    platform_counts = df["UTM Platform"].value_counts().to_dict()
    
    # Sort platforms by order count (descending)
    sorted_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
    platforms = [p[0] for p in sorted_platforms]
    
    platform_icons = {
        'Meta': '📱',
        'Google': '🔍',
        'Organic': '🌱',
        'Email': '📧',
        'WhatsApp': '💬',
        'Twitter': '🐦',
        'LinkedIn': '💼',
        'Other': '🔗'
    }
    
    if 'selected_platform' not in st.session_state:
        st.session_state.selected_platform = None
    
    cols = st.columns(min(len(platforms), 8))
    
    for idx, platform in enumerate(platforms[:8]):
        with cols[idx]:
            count = platform_counts.get(platform, 0)
            if st.button(f"{platform_icons.get(platform, '•')} {platform}\n({count:,})", 
                       key=f"btn_{platform}",
                       use_container_width=True):
                st.session_state.selected_platform = platform
                st.rerun()

# ------------ SIDEBAR FILTERS ------------
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    valid_dates = df[df["Order Date"].notna()]
    
    if len(valid_dates) == 0:
        st.error("No valid dates found in data")
        st.stop()
    
    min_date = valid_dates["Order Date"].min().date()
    max_date = valid_dates["Order Date"].max().date()
    
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
    
    # City Tier filter
    if "City Tier" in df.columns:
        tier_filter = st.multiselect(
            "City Tier",
            ["Tier 1", "Tier 2", "Tier 3"],
            default=["Tier 1", "Tier 2", "Tier 3"]
        )
    else:
        tier_filter = []
    
    # Platform filter
    if "UTM Platform" in df.columns:
        platforms_list = df["UTM Platform"].unique().tolist()
        
        if 'selected_platform' in st.session_state and st.session_state.selected_platform:
            default_platforms = [st.session_state.selected_platform]
        else:
            default_platforms = platforms_list
        
        platform_filter = st.multiselect(
            "Platform (UTM Source)",
            platforms_list,
            default=default_platforms
        )
    else:
        platform_filter = []
    
    # UTM Source filter
    if "Utm Source" in df.columns:
        utm_sources = df["Utm Source"].dropna().unique().tolist()
        if utm_sources:
            utm_filter = st.multiselect(
                "UTM Source",
                utm_sources,
                default=utm_sources
            )
        else:
            utm_filter = []
    else:
        utm_filter = []
    
    # UTM Content filter - NEW
    if "Utm Content" in df.columns:
        utm_content_data = df.groupby("Utm Content")["Order Number"].count().reset_index()
        utm_content_data.columns = ["Content", "Orders"]
        utm_content_data = utm_content_data.sort_values("Orders", ascending=False).head(10)
        utm_contents = utm_content_data["Content"].tolist()
        
        if utm_contents:
            utm_content_filter = st.multiselect(
                "UTM Content (Top 10)",
                utm_contents,
                default=utm_contents
            )
        else:
            utm_content_filter = []
    else:
        utm_content_filter = []
    
    st.markdown("---")
    
    # Time granularity
    st.markdown("### 📅 Time Granularity")
    time_grain = st.selectbox(
        "Select View",
        ["Daily", "Weekly", "Monthly", "Yearly"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📊 Dashboard Info")
    st.info(f"**Last Updated:** {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

# ------------ APPLY FILTERS ------------
filtered = df[
    (df["Order Date"].dt.date >= date_range[0]) &
    (df["Order Date"].dt.date <= date_range[1]) &
    (df["Status"].isin(status_filter)) &
    (df["Payment Type"].isin(payment_filter))
]

if tier_filter and "City Tier" in filtered.columns:
    filtered = filtered[filtered["City Tier"].isin(tier_filter)]

if platform_filter and "UTM Platform" in filtered.columns:
    filtered = filtered[filtered["UTM Platform"].isin(platform_filter)]

if utm_filter and "Utm Source" in filtered.columns:
    filtered = filtered[filtered["Utm Source"].isin(utm_filter)]

# NEW: Apply UTM Content filter
if utm_content_filter and "Utm Content" in filtered.columns:
    filtered = filtered[filtered["Utm Content"].isin(utm_content_filter)]

# ------------ KEY METRICS ------------
st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

total_orders = filtered["Order Number"].nunique()
total_revenue = filtered["Grand Total"].sum()
avg_order_value = filtered["Grand Total"].mean()
prepaid_orders = filtered[filtered["Payment Type"] == "Prepaid"].shape[0]
cod_orders = filtered[filtered["Payment Type"] == "COD"].shape[0]

confirmed_orders = filtered[filtered["Status"].str.contains("Confirmed|Delivered|Shipped", case=False, na=False)].shape[0]
total_transactions = len(filtered)
payment_success_ratio = (confirmed_orders / total_transactions * 100) if total_transactions > 0 else 0

with col1:
    st.markdown(create_metric_card("Total Orders", f"{total_orders:,}"), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card("Total Revenue", f"₹{total_revenue:,.0f}"), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card("Avg Order Value", f"₹{avg_order_value:,.0f}"), unsafe_allow_html=True)

with col4:
    st.markdown(create_metric_card("Prepaid Orders", f"{prepaid_orders:,}"), unsafe_html=True)

with col5:
    st.markdown(create_metric_card("COD Orders", f"{cod_orders:,}"), unsafe_html=True)

with col6:
    st.markdown(create_metric_card("Payment Success", f"{payment_success_ratio:.1f}%"), unsafe_html=True)

# ------------ ROW 1: TRENDS ------------
st.markdown('<div class="section-header">📊 Revenue & Order Trends</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Dynamic trend based on time granularity
    if time_grain == "Daily":
        daily = filtered.groupby(filtered["Order Date"].dt.date).agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        daily.columns = ["Date", "Revenue", "Orders"]
        x_data = daily["Date"]
        title_text = "Daily Revenue & Orders"
    elif time_grain == "Weekly":
        filtered["Week"] = filtered["Order Date"].dt.to_period('W').dt.start_time
        daily = filtered.groupby("Week").agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        daily.columns = ["Date", "Revenue", "Orders"]
        x_data = daily["Date"]
        title_text = "Weekly Revenue & Orders"
    elif time_grain == "Monthly":
        filtered["Month"] = filtered["Order Date"].dt.to_period('M').dt.start_time
        daily = filtered.groupby("Month").agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        daily.columns = ["Date", "Revenue", "Orders"]
        x_data = daily["Date"]
        title_text = "Monthly Revenue & Orders"
    else:
        filtered["Year"] = filtered["Order Date"].dt.year
        daily = filtered.groupby("Year").agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        daily.columns = ["Date", "Revenue", "Orders"]
        x_data = daily["Date"]
        title_text = "Yearly Revenue & Orders"
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=x_data, 
            y=daily["Revenue"],
            name="Revenue",
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=x_data, 
            y=daily["Orders"],
            name="Orders",
            line=dict(color='#f093fb', width=2, dash='dot'),
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=16, color='#1a1a1a')),
        height=400,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
        margin=dict(l=60, r=60, t=60, b=60)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0', secondary_y=False)
    fig.update_yaxes(showgrid=False, secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # COD vs Prepaid visualization
    payment_split = filtered.groupby("Payment Type").agg({
        "Order Number": "count",
        "Grand Total": "sum"
    }).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=payment_split["Payment Type"],
        y=payment_split["Order Number"],
        name="Orders",
        marker=dict(color=['#4facfe', '#f093fb']),
        text=payment_split["Order Number"],
        textposition='outside',
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=payment_split["Payment Type"],
        y=payment_split["Grand Total"] / payment_split["Order Number"],
        name="AOV",
        mode='lines+markers',
        marker=dict(color='#fee140', size=12),
        line=dict(color='#fee140', width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=dict(text="Payment Type: Orders & AOV", font=dict(size=16, color='#1a1a1a')),
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders"),
        yaxis2=dict(showgrid=False, overlaying='y', side='right', title="AOV (₹)"),
        font=dict(family="Arial, sans-serif", size=14, color='#1a1a1a'),
        margin=dict(l=60, r=60, t=60, b=60),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ------------ ROW 2: MAP & TIER ANALYSIS ------------
st.markdown('<div class="section-header">🗺️ Geographic Analysis & City Tiers</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # India Map
    if "Billing State" in filtered.columns:
        state_data = filtered.groupby("Billing State").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        state_data.columns = ["State", "Orders", "Revenue"]
        
        #
