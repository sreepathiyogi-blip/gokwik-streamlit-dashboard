import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import date, datetime
import hashlib

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="GoKwik Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
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
    
    pincode_str = str(pincode).strip()[:3]
    
    try:
        pincode_prefix = int(pincode_str)
    except:
        return 'Unknown'
    
    # Tier 1 cities pincodes (Major metros)
    tier_1_pincodes = [
        400, 401, 110, 121, 122, 201, 122, 124, 125, 127, 128, 134,
        560, 562, 563, 500, 501, 502, 503, 504, 505, 508,
        600, 601, 602, 603, 700, 711, 712, 713, 721, 722, 743,
        411, 412, 380, 382, 383,
    ]
    
    # Tier 2 cities pincodes
    tier_2_pincodes = [
        302, 303, 226, 227, 208, 209, 440, 441, 442,
        452, 453, 462, 463, 530, 531, 390, 391,
        141, 142, 282, 283, 422, 423, 121,
        250, 251, 360, 361, 221, 222, 190, 191, 192, 193, 194,
        143, 211, 212, 834, 835, 711, 641, 642,
        520, 521, 342, 344, 625, 626, 492, 493,
        324, 325, 781, 782, 783, 160, 140, 122, 201,
    ]
    
    if pincode_prefix in tier_1_pincodes:
        return 'Tier 1'
    elif pincode_prefix in tier_2_pincodes:
        return 'Tier 2'
    else:
        return 'Tier 3'

# ---------------- HEADER ----------------
st.markdown("""
<div class="dashboard-header">
    <h1>📊 GoKwik Order Analytics Dashboard</h1>
    <p>Real-time insights into your e-commerce performance</p>
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
    
    if uploaded_file:
        st.success("✅ File uploaded successfully")

# ---------------- UPLOAD PROCESSING ----------------
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
    
    # City tier classification
    if "Billing Pincode" in df.columns:
        df["City Tier"] = df["Billing Pincode"].apply(get_city_tier)
    elif "Shipping Pincode" in df.columns:
        df["City Tier"] = df["Shipping Pincode"].apply(get_city_tier)
    else:
        df["City Tier"] = "Unknown"

    save_data(df)
    with st.sidebar:
        st.success("✅ Data processed successfully")

# ---------------- LOAD DATA ----------------
if not uploaded_file:
    df = load_data()
    if df is None:
        st.info("👆 Please upload a file to view the dashboard")
        st.stop()

if "Order Date" not in df.columns:
    st.error("⚠️ Data corrupted. Please re-upload the file.")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
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
    
    # Campaign filter removed
    campaign_filter = []
    
    st.markdown("---")
    
    # Time granularity selector
    st.markdown("### 📅 Time Granularity")
    time_grain = st.selectbox(
        "Select View",
        ["Daily", "Weekly", "Monthly", "Yearly"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📊 Dashboard Info")
    st.info(f"**Last Updated:** {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

# ---------------- APPLY FILTERS ----------------
filtered = df[
    (df["Order Date"].dt.date >= date_range[0]) &
    (df["Order Date"].dt.date <= date_range[1]) &
    (df["Status"].isin(status_filter)) &
    (df["Payment Type"].isin(payment_filter))
]

if tier_filter and "City Tier" in filtered.columns:
    filtered = filtered[filtered["City Tier"].isin(tier_filter)]

if utm_filter and "Utm Source" in filtered.columns:
    filtered = filtered[filtered["Utm Source"].isin(utm_filter)]

if campaign_filter and "Utm Campaign" in filtered.columns:
    filtered = filtered[filtered["Utm Campaign"].isin(campaign_filter)]

# ---------------- KEY METRICS ----------------
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
    st.markdown(create_metric_card("Prepaid Orders", f"{prepaid_orders:,}"), unsafe_allow_html=True)

with col5:
    st.markdown(create_metric_card("COD Orders", f"{cod_orders:,}"), unsafe_allow_html=True)

with col6:
    st.markdown(create_metric_card("Payment Success", f"{payment_success_ratio:.1f}%"), unsafe_allow_html=True)

# ---------------- ROW 1: TRENDS WITH DRILL-DOWN ----------------
st.markdown('<div class="section-header">📊 Revenue & Order Trends</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
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
        title=dict(text=title_text, font=dict(size=16, color='#1a1a1a', family="Arial, sans-serif")),
        height=400,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
        margin=dict(l=60, r=60, t=60, b=60)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0', tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a'))
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0', secondary_y=False, tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a'))
    fig.update_yaxes(showgrid=False, secondary_y=True, tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a'))
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    payment_split = filtered.groupby("Payment Type").agg({
        "Order Number": "count",
        "Grand Total": "sum"
    }).reset_index()
    
    fig = go.Figure(data=[go.Pie(
        labels=payment_split["Payment Type"],
        values=payment_split["Order Number"],
        hole=0.5,
        marker=dict(colors=['#4facfe', '#f093fb']),
        textinfo='label+percent+value',
        textfont_size=16,
        textfont_color='white',
        textposition='inside'
    )])
    
    fig.update_layout(
        title=dict(text="Payment Split", font=dict(size=16, color='#1a1a1a', family="Arial, sans-serif")),
        height=400,
        showlegend=False,
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=14, color='#1a1a1a'),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 2: MAP & TIER ANALYSIS ----------------
st.markdown('<div class="section-header">🗺️ Geographic Analysis & City Tiers</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 0.001])

with col1:
    # State coordinates mapping
    state_coords = {
        'ANDHRA PRADESH': (15.9129, 79.74),
        'ARUNACHAL PRADESH': (28.218, 94.7278),
        'ASSAM': (26.2006, 92.9376),
        'BIHAR': (25.0961, 85.3131),
        'CHHATTISGARH': (21.2787, 81.8661),
        'GOA': (15.2993, 74.124),
        'GUJARAT': (22.2587, 71.1924),
        'HARYANA': (29.0588, 76.0856),
        'HIMACHAL PRADESH': (31.1048, 77.1734),
        'JHARKHAND': (23.6102, 85.2799),
        'KARNATAKA': (15.3173, 75.7139),
        'KERALA': (10.8505, 76.2711),
        'MADHYA PRADESH': (22.9734, 78.6569),
        'MAHARASHTRA': (19.7515, 75.7139),
        'MANIPUR': (24.6637, 93.9063),
        'MEGHALAYA': (25.467, 91.3662),
        'MIZORAM': (23.1645, 92.9376),
        'NAGALAND': (26.1584, 94.5624),
        'ODISHA': (20.9517, 85.0985),
        'PUNJAB': (31.1471, 75.3412),
        'RAJASTHAN': (27.0238, 74.2179),
        'SIKKIM': (27.533, 88.5122),
        'TAMIL NADU': (11.1271, 78.6569),
        'TELANGANA': (18.1124, 79.0193),
        'TRIPURA': (23.9408, 91.9882),
        'UTTAR PRADESH': (26.8467, 80.9462),
        'UTTARAKHAND': (30.0668, 79.0193),
        'WEST BENGAL': (22.9868, 87.855),
        'DELHI': (28.7041, 77.1025),
        'JAMMU AND KASHMIR': (33.7782, 76.5762),
        'LADAKH': (34.1526, 77.577),
        'PUDUCHERRY': (11.9416, 79.8083),
        'CHANDIGARH': (30.7333, 76.7794),
        'DADRA AND NAGAR HAVELI': (20.1809, 73.0169),
        'DAMAN AND DIU': (20.4283, 72.8397),
        'LAKSHADWEEP': (10.5667, 72.6417),
        'ANDAMAN AND NICOBAR': (11.7401, 92.6586)
    }
    
    if "Billing State" in filtered.columns:
        state_data = filtered.groupby("Billing State").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        state_data.columns = ["State", "Orders", "Revenue"]
        state_data["State_Clean"] = state_data["State"].str.title().str.strip()
        
        # Prepare map data
        map_state_data = state_data.copy()
        map_state_data["State_Upper"] = map_state_data["State"].str.upper().str.strip()
        
        # Match coordinates
        lats = []
        lons = []
        matched_orders = []
        matched_states = []
        
        for idx, row in map_state_data.iterrows():
            state_name = row["State_Upper"]
            if state_name in state_coords:
                lat, lon = state_coords[state_name]
                lats.append(lat)
                lons.append(lon)
                matched_orders.append(row["Orders"])
                matched_states.append(row["State_Clean"])
        
        # Create the map figure
        if len(lats) > 0:
            max_orders = max(matched_orders) if matched_orders else 1
            
            fig = go.Figure()
            
            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                text=matched_states,
                marker=dict(
                    size=[o / max_orders * 50 + 10 for o in matched_orders],
                    color=matched_orders,
                    colorscale='Blues',
                    showscale=True,
                    colorbar=dict(title="Orders", x=1.1),
                    line=dict(width=1, color='white'),
                    sizemode='diameter'
                ),
                customdata=matched_orders,
                hovertemplate='<b>%{text}</b><br>Orders: %{customdata:,.0f}<br><extra></extra>',
                showlegend=False
            ))
            
            fig.update_geos(
                visible=True,
                resolution=50,
                scope="asia",
                showcountries=True,
                countrycolor="lightgray",
                showsubunits=True,
                subunitcolor="white",
                lonaxis_range=[68, 97],
                lataxis_range=[8, 37],
                bgcolor='rgba(240,240,240,0.3)',
                projection_type="mercator"
            )
            
            fig.update_layout(
                title=dict(text="State-wise Order Distribution (India Map)", font=dict(size=16, color='#1a1a1a')),
                height=400,
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)

with col2:
    # State coordinates mapping
    state_coords = {
        'ANDHRA PRADESH': (15.9129, 79.74),
        'ARUNACHAL PRADESH': (28.218, 94.7278),
        'ASSAM': (26.2006, 92.9376),
        'BIHAR': (25.0961, 85.3131),
        'CHHATTISGARH': (21.2787, 81.8661),
        'GOA': (15.2993, 74.124),
        'GUJARAT': (22.2587, 71.1924),
        'HARYANA': (29.0588, 76.0856),
        'HIMACHAL PRADESH': (31.1048, 77.1734),
        'JHARKHAND': (23.6102, 85.2799),
        'KARNATAKA': (15.3173, 75.7139),
        'KERALA': (10.8505, 76.2711),
        'MADHYA PRADESH': (22.9734, 78.6569),
        'MAHARASHTRA': (19.7515, 75.7139),
        'MANIPUR': (24.6637, 93.9063),
        'MEGHALAYA': (25.467, 91.3662),
        'MIZORAM': (23.1645, 92.9376),
        'NAGALAND': (26.1584, 94.5624),
        'ODISHA': (20.9517, 85.0985),
        'PUNJAB': (31.1471, 75.3412),
        'RAJASTHAN': (27.0238, 74.2179),
        'SIKKIM': (27.533, 88.5122),
        'TAMIL NADU': (11.1271, 78.6569),
        'TELANGANA': (18.1124, 79.0193),
        'TRIPURA': (23.9408, 91.9882),
        'UTTAR PRADESH': (26.8467, 80.9462),
        'UTTARAKHAND': (30.0668, 79.0193),
        'WEST BENGAL': (22.9868, 87.855),
        'DELHI': (28.7041, 77.1025),
        'JAMMU AND KASHMIR': (33.7782, 76.5762),
        'LADAKH': (34.1526, 77.577),
        'PUDUCHERRY': (11.9416, 79.8083),
        'CHANDIGARH': (30.7333, 76.7794),
        'DADRA AND NAGAR HAVELI': (20.1809, 73.0169),
        'DAMAN AND DIU': (20.4283, 72.8397),
        'LAKSHADWEEP': (10.5667, 72.6417),
        'ANDAMAN AND NICOBAR': (11.7401, 92.6586)
    }
    
    if "City Tier" in filtered.columns:
        # Prepare map data
        map_state_data = state_data.copy()
        map_state_data["State_Upper"] = map_state_data["State"].str.upper().str.strip()
        
        # Match coordinates
        lats = []
        lons = []
        matched_orders = []
        matched_states = []
        
        for idx, row in map_state_data.iterrows():
            state_name = row["State_Upper"]
            if state_name in state_coords:
                lat, lon = state_coords[state_name]
                lats.append(lat)
                lons.append(lon)
                matched_orders.append(row["Orders"])
                matched_states.append(row["State_Clean"])
        
        # Create the map figure
        if len(lats) > 0:
            max_orders = max(matched_orders) if matched_orders else 1
            
            fig = go.Figure()
            
            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                text=matched_states,
                marker=dict(
                    size=[o / max_orders * 50 + 10 for o in matched_orders],
                    color=matched_orders,
                    colorscale='Blues',
                    showscale=True,
                    colorbar=dict(title="Orders", x=1.1),
                    line=dict(width=1, color='white'),
                    sizemode='diameter'
                ),
                customdata=matched_orders,
                hovertemplate='<b>%{text}</b><br>Orders: %{customdata:,.0f}<br><extra></extra>',
                showlegend=False
            ))
            
            fig.update_geos(
                visible=True,
                resolution=50,
                scope="asia",
                showcountries=True,
                countrycolor="lightgray",
                showsubunits=True,
                subunitcolor="white",
                lonaxis_range=[68, 97],
                lataxis_range=[8, 37],
                bgcolor='rgba(240,240,240,0.3)',
                projection_type="mercator"
            )
            
            fig.update_layout(
                title=dict(text="State-wise Order Distribution (India Map)", font=dict(size=16, color='#1a1a1a')),
                height=400,
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 3: TOP 10 WITH TOGGLE ----------------
st.markdown('<div class="section-header">🏆 Top 10 States Performance</div>', unsafe_allow_html=True)

if "Billing State" in filtered.columns:
    col1, col2 = st.columns([3, 1])
    
    with col2:
        top10_metric = st.radio(
            "Select Metric",
            ["Orders", "Revenue"],
            horizontal=True
        )
    
    with col1:
        state_data = filtered.groupby("Billing State").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        state_data.columns = ["State", "Orders", "Revenue"]
        
        if top10_metric == "Orders":
            state_data = state_data.sort_values("Orders", ascending=True).tail(10)
            y_data = state_data["Orders"]
            color_data = state_data["Orders"]
            title_text = "Top 10 States by Orders"
            text_data = state_data["Orders"]
        else:
            state_data = state_data.sort_values("Revenue", ascending=True).tail(10)
            y_data = state_data["Revenue"]
            color_data = state_data["Revenue"]
            title_text = "Top 10 States by Revenue"
            text_data = [f"₹{x:,.0f}" for x in state_data["Revenue"]]
        
        fig = go.Figure(go.Bar(
            x=y_data,
            y=state_data["State"],
            orientation='h',
            marker=dict(color=color_data, colorscale='Viridis', showscale=False),
            text=text_data,
            textposition='outside'
        ))
        
        fig.update_layout(
            title=dict(text=title_text, font=dict(size=16, color='#1a1a1a')),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0', tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis=dict(showgrid=False, tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
            margin=dict(l=60, r=60, t=60, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 4: UTM CONTENT & CAMPAIGN ANALYSIS ----------------
st.markdown('<div class="section-header">📱 Marketing Performance Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 0.001])

with col1:
    if "Utm Content" in filtered.columns:
        st.markdown("#### Top 10 UTM Content: COD vs Prepaid")
        
        utm_content_data = filtered.groupby(["Utm Content", "Payment Type"]).agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        
        top_contents = filtered.groupby("Utm Content")["Order Number"].count().nlargest(10).index.tolist()
        utm_content_data = utm_content_data[utm_content_data["Utm Content"].isin(top_contents)]
        
        # Pivot to create table
        table_data = utm_content_data.pivot_table(
            index="Utm Content",
            columns="Payment Type",
            values="Order Number",
            fill_value=0
        ).reset_index()
        
        # Ensure both columns exist
        if "Prepaid" not in table_data.columns:
            table_data["Prepaid"] = 0
        if "COD" not in table_data.columns:
            table_data["COD"] = 0
        
        # Add total column
        table_data["Total Orders"] = table_data["Prepaid"] + table_data["COD"]
        table_data["Prepaid %"] = (table_data["Prepaid"] / table_data["Total Orders"] * 100).round(1)
        table_data["COD %"] = (table_data["COD"] / table_data["Total Orders"] * 100).round(1)
        
        # Sort by total orders
        table_data = table_data.sort_values("Total Orders", ascending=False)
        
        # Reorder columns
        table_data = table_data[["Utm Content", "Prepaid", "COD", "Total Orders", "Prepaid %", "COD %"]]
        
        st.dataframe(
            table_data.style.format({
                "Prepaid": "{:,.0f}",
                "COD": "{:,.0f}",
                "Total Orders": "{:,.0f}",
                "Prepaid %": "{:.1f}%",
                "COD %": "{:.1f}%"
            }),
            use_container_width=True,
            height=400,
            hide_index=True
        )
    elif "Utm Source" in filtered.columns:
        utm_data = filtered.groupby("Utm Source").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        utm_data.columns = ["Source", "Orders", "Revenue"]
        utm_data = utm_data.sort_values("Orders", ascending=False).head(10)
        utm_data["AOV"] = utm_data["Revenue"] / utm_data["Orders"]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=utm_data["Source"],
            y=utm_data["Orders"],
            name="Orders",
            marker=dict(color='#667eea'),
            text=utm_data["Orders"],
            textposition='outside',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=utm_data["Source"],
            y=utm_data["AOV"],
            name="AOV",
            mode='lines+markers',
            marker=dict(color='#f093fb', size=10),
            line=dict(color='#f093fb', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=dict(text="UTM Source Performance: Orders & AOV", font=dict(size=16, color='#1a1a1a')),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, title="Source", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis2=dict(showgrid=False, overlaying='y', side='right', title="AOV (₹)", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=60, r=60, t=60, b=60),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#1a1a1a'))
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    pass

# ---------------- ROW 5: RFM ANALYSIS ----------------
st.markdown('<div class="section-header">🎯 RFM Analysis (Recency, Frequency, Monetary)</div>', unsafe_allow_html=True)

if "Customer ID" in filtered.columns:
    current_date = filtered["Order Date"].max()
    
    rfm_data = filtered.groupby("Customer ID").agg({
        "Order Date": lambda x: (current_date - x.max()).days,
        "Order Number": "count",
        "Grand Total": "sum"
    }).reset_index()
    
    rfm_data.columns = ["Customer ID", "Recency", "Frequency", "Monetary"]
    
    def calculate_score(data, column, ascending=True):
        try:
            unique_values = data[column].nunique()
            if unique_values <= 1:
                return pd.Series([3] * len(data), index=data.index)
            
            n_bins = min(5, unique_values)
            if ascending:
                labels = list(range(1, n_bins + 1))
            else:
                labels = list(range(n_bins, 0, -1))
            
            if column == "Frequency":
                return pd.qcut(data[column].rank(method='first'), n_bins, labels=labels, duplicates='drop')
            else:
                return pd.qcut(data[column], n_bins, labels=labels, duplicates='drop')
        except:
            try:
                if column == "Frequency":
                    return pd.cut(data[column].rank(method='first'), n_bins, labels=labels, duplicates='drop')
                else:
                    return pd.cut(data[column], n_bins, labels=labels, duplicates='drop')
            except:
                ranks = data[column].rank(method='first', pct=True)
                if ascending:
                    return pd.cut(ranks, bins=5, labels=[1, 2, 3, 4, 5])
                else:
                    return pd.cut(ranks, bins=5, labels=[5, 4, 3, 2, 1])
    
    rfm_data["R_Score"] = calculate_score(rfm_data, "Recency", ascending=False)
    rfm_data["F_Score"] = calculate_score(rfm_data, "Frequency", ascending=True)
    rfm_data["M_Score"] = calculate_score(rfm_data, "Monetary", ascending=True)
    
    rfm_data["RFM_Score"] = rfm_data["R_Score"].astype(str) + rfm_data["F_Score"].astype(str) + rfm_data["M_Score"].astype(str)
    rfm_data["RFM_Total"] = rfm_data["R_Score"].astype(int) + rfm_data["F_Score"].astype(int) + rfm_data["M_Score"].astype(int)
    
    def segment_customer(score):
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
    
    rfm_data["Segment"] = rfm_data["RFM_Total"].apply(segment_customer)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        segment_counts = rfm_data["Segment"].value_counts().reset_index()
        segment_counts.columns = ["Segment", "Customers"]
        
        color_map = {
            "Champions": "#43e97b",
            "Loyal": "#30cfd0",
            "Potential": "#fee140",
            "At Risk": "#fa709a",
            "Lost": "#f093fb"
        }
        
        colors = [color_map.get(seg, "#667eea") for seg in segment_counts["Segment"]]
        
        fig = go.Figure(data=[go.Bar(
            x=segment_counts["Segment"],
            y=segment_counts["Customers"],
            marker=dict(color=colors),
            text=segment_counts["Customers"],
            textposition='outside'
        )])
        
        fig.update_layout(
            title=dict(text="Customer Segmentation (RFM)", font=dict(size=15, color='#1a1a1a')),
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Customers", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(data=[go.Histogram(
            x=rfm_data["Recency"],
            nbinsx=30,
            marker=dict(color='#667eea', line=dict(color='white', width=1))
        )])
        
        fig.update_layout(
            title=dict(text="Recency Distribution (Days)", font=dict(size=15, color='#1a1a1a')),
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(title="Days Since Last Order", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis=dict(title="Customers", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=rfm_data["Frequency"],
            y=rfm_data["Monetary"],
            mode='markers',
            marker=dict(
                size=rfm_data["RFM_Total"] * 2,
                color=rfm_data["RFM_Total"],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="RFM Score"),
                line=dict(color='white', width=0.5)
            ),
            text=rfm_data["Customer ID"],
            hovertemplate='<b>%{text}</b><br>Orders: %{x}<br>Revenue: ₹%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text="Frequency vs Monetary Value", font=dict(size=15, color='#1a1a1a')),
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Frequency (Orders)", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Monetary (₹)", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 6: TOP 15 CUSTOMERS ----------------
st.markdown('<div class="section-header">👥 Top 15 Customers by Lifetime Value</div>', unsafe_allow_html=True)

if "Customer ID" in filtered.columns:
    clv_data = df.groupby("Customer ID").agg({
        "Order Number": "count",
        "Grand Total": "sum",
        "Order Date": ["min", "max"]
    }).reset_index()
    
    clv_data.columns = ["Customer ID", "Total Orders", "Total Revenue", "First Order", "Last Order"]
    clv_data = clv_data.sort_values("Total Revenue", ascending=False).head(15)
    
    col1, col2 = st.columns([1, 0.001])
    
    with col1:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=clv_data["Customer ID"],
            y=clv_data["Total Revenue"],
            name="Total Revenue",
            marker=dict(color='#667eea'),
            text=[f"₹{x:,.0f}" for x in clv_data["Total Revenue"]],
            textposition='outside',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=clv_data["Customer ID"],
            y=clv_data["Total Orders"],
            name="Orders",
            mode='lines+markers',
            marker=dict(color='#f093fb', size=10),
            line=dict(color='#f093fb', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=dict(text="Top 15 Customers: Revenue & Orders", font=dict(size=16, color='#1a1a1a')),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickangle=-45, title="Customer ID (Hashed)", tickfont=dict(color='#1a1a1a', size=9), title_font=dict(color='#1a1a1a')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Total Revenue (₹)", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis2=dict(showgrid=False, overlaying='y', side='right', title="Total Orders", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            font=dict(family="Arial, sans-serif", size=10, color='#1a1a1a'),
            margin=dict(l=60, r=60, t=60, b=120),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#1a1a1a'))
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        display_clv = clv_data[["Customer ID", "Total Orders", "Total Revenue"]].copy()
        display_clv["Total Revenue"] = display_clv["Total Revenue"].apply(lambda x: f"₹{x:,.0f}")
        
        st.dataframe(display_clv, use_container_width=True, height=400, hide_index=True)

# ---------------- ROW 7: PRODUCTS & PAYMENT MIX ----------------
st.markdown('<div class="section-header">🛍️ Product Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 0.001])

with col1:
    if "Product Name" in filtered.columns:
        product_data = filtered.groupby("Product Name").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        product_data.columns = ["Product", "Orders", "Revenue"]
        product_data = product_data.sort_values("Orders", ascending=False).head(10)
        
        fig = go.Figure(data=[go.Bar(
            x=product_data["Product"],
            y=product_data["Orders"],
            marker=dict(color=product_data["Revenue"], colorscale='Viridis', showscale=True, colorbar=dict(title="Revenue (₹)")),
            text=product_data["Orders"],
            textposition='outside'
        )])
        
        fig.update_layout(
            title=dict(text="Top 10 Products by Orders", font=dict(size=16, color='#1a1a1a')),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
            margin=dict(l=60, r=60, t=60, b=100)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if "Product Name" in filtered.columns:
        product_payment = filtered.groupby(["Product Name", "Payment Type"]).agg({
            "Order Number": "count"
        }).reset_index()
        
        top_products = filtered.groupby("Product Name")["Order Number"].count().nlargest(8).index.tolist()
        product_payment = product_payment[product_payment["Product Name"].isin(top_products)]
        
        fig = go.Figure()
        
        for payment_type in ["Prepaid", "COD"]:
            data = product_payment[product_payment["Payment Type"] == payment_type]
            fig.add_trace(go.Bar(
                name=payment_type,
                x=data["Product Name"],
                y=data["Order Number"],
                marker=dict(color='#4facfe' if payment_type == "Prepaid" else '#f093fb')
            ))
        
        fig.update_layout(
            title=dict(text="Product-wise Payment Split (Top 8)", font=dict(size=16, color='#1a1a1a')),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            barmode='stack',
            xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=60, r=60, t=60, b=100),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#1a1a1a'))
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- DATA TABLE ----------------
st.markdown('<div class="section-header">📋 Detailed Order Data</div>', unsafe_allow_html=True)

display_cols = [
    "Order Number", "Order Date", "Status", "Payment Method", 
    "Grand Total", "Customer ID", "Billing State", "Billing City", 
    "Billing Pincode", "City Tier", "Product Name", "Utm Source", "Utm Campaign", "Utm Content"
]
display_cols = [col for col in display_cols if col in filtered.columns]

st.dataframe(
    filtered[display_cols].style.format({
        "Grand Total": "₹{:,.0f}",
        "Order Date": lambda x: x.strftime("%d %b %Y") if pd.notnull(x) else ""
    }),
    use_container_width=True,
    height=400
)

# ---------------- DOWNLOAD ----------------
st.markdown('<div class="section-header">⬇️ Export Data</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    st.download_button(
        "📥 Download CSV",
        filtered.drop(columns=["__last_updated__"], errors='ignore').to_csv(index=False),
        file_name=f"gokwik_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    st.download_button(
        "📊 Download Excel",
        filtered.drop(columns=["__last_updated__"], errors='ignore').to_csv(index=False),
        file_name=f"gokwik_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>GoKwik Order Analytics Dashboard | Built with Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)
