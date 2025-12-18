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
    page_title="GoKwik Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- ENHANCED CUSTOM CSS ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main background with modern gradient */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .block-container {
        max-width: 100%;
        padding: 2rem 3rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        margin: 1rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    /* Enhanced metric cards with glassmorphism */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
        backdrop-filter: blur(10px);
        padding: 28px;
        border-radius: 18px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        text-align: center;
        margin: 10px 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }
    
    .metric-card:hover::before {
        transform: scaleX(1);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 48px rgba(102, 126, 234, 0.35);
        background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 0.9) 100%);
    }
    
    /* Animated metric values */
    .metric-value {
        font-size: 42px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 12px 0;
        text-shadow: none;
        letter-spacing: -1px;
    }
    
    /* Enhanced metric labels */
    .metric-label {
        font-size: 12px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    /* Modern header with gradient */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 50px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .dashboard-header h1 {
        font-size: 48px;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        position: relative;
        z-index: 1;
    }
    
    .dashboard-header p {
        font-size: 18px;
        margin-top: 10px;
        opacity: 0.95;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    /* Modern section headers */
    .section-header {
        font-size: 26px;
        font-weight: 700;
        color: #1e293b;
        margin: 45px 0 28px 0;
        padding: 25px 30px;
        border-left: 0;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Enhanced chart containers */
    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        background: white;
        margin: 12px 0;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Modern sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label {
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Enhanced buttons */
    .stButton>button {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 700;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        width: 100%;
        height: auto;
        min-height: 85px;
        font-size: 13px;
        white-space: pre-line;
        line-height: 1.5;
        backdrop-filter: blur(10px);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(255, 255, 255, 0.25);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* Enhanced dataframe */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }
        
        .metric-card {
            padding: 18px;
            min-height: 130px;
        }
        
        .metric-value {
            font-size: 32px;
        }
        
        .dashboard-header h1 {
            font-size: 32px;
        }
        
        .section-header {
            font-size: 20px;
            padding: 18px 20px;
        }
    }
    
    /* Loading animation */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
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

def create_metric_card(label, value, delta=None, delta_color="normal", icon=""):
    """Enhanced metric card with icons and better styling"""
    delta_html = ""
    if delta:
        delta_symbol = "▲" if delta_color == "normal" else "▼"
        color = "#10b981" if delta_color == "normal" else "#ef4444"
        delta_html = f'<div style="color: {color}; font-size: 15px; font-weight: 700; margin-top: 10px;">{delta_symbol} {delta}</div>'
    
    return f"""
    <div class="metric-card">
        <div style="font-size: 32px; margin-bottom: 8px; opacity: 0.8;">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def get_city_tier(pincode):
    """Enhanced pincode to city tier classification with more comprehensive coverage"""
    if pd.isna(pincode):
        return 'Unknown'
    
    pincode_str = str(pincode).strip()[:3]
    
    try:
        pincode_prefix = int(pincode_str)
    except:
        return 'Unknown'
    
    # Tier 1 cities (Metro cities with prefix ranges)
    tier_1_ranges = [
        # Mumbai & Navi Mumbai
        (400, 401),
        # Delhi NCR
        (110, 110), (121, 122), (124, 125), (127, 128), (134, 134), (201, 201),
        # Bangalore
        (560, 563),
        # Hyderabad
        (500, 509),
        # Chennai
        (600, 603),
        # Kolkata
        (700, 700), (711, 713), (721, 722), (743, 743),
        # Pune
        (411, 412),
        # Ahmedabad
        (380, 383),
    ]
    
    # Tier 2 cities (Major cities)
    tier_2_ranges = [
        # Jaipur
        (302, 303),
        # Lucknow
        (226, 227),
        # Kanpur
        (208, 209),
        # Nagpur
        (440, 442),
        # Indore
        (452, 453),
        # Bhopal
        (462, 463),
        # Visakhapatnam
        (530, 531),
        # Vadodara
        (390, 391),
        # Ludhiana
        (141, 142),
        # Agra
        (282, 283),
        # Nashik
        (422, 423),
        # Meerut
        (250, 251),
        # Rajkot
        (360, 361),
        # Varanasi
        (221, 222),
        # Srinagar
        (190, 194),
        # Amritsar
        (143, 143),
        # Allahabad/Prayagraj
        (211, 212),
        # Ranchi
        (834, 835),
        # Coimbatore
        (641, 642),
        # Vijayawada
        (520, 521),
        # Jodhpur
        (342, 344),
        # Madurai
        (625, 626),
        # Raipur
        (492, 493),
        # Kota
        (324, 325),
        # Guwahati
        (781, 783),
        # Chandigarh
        (160, 160), (140, 140),
        # Patna
        (800, 801),
        # Bhubaneswar
        (751, 752),
        # Thiruvananthapuram
        (695, 695),
        # Kochi
        (682, 683),
        # Mysore
        (570, 571),
        # Surat
        (394, 395),
    ]
    
    # Check Tier 1
    for start, end in tier_1_ranges:
        if start <= pincode_prefix <= end:
            return 'Tier 1'
    
    # Check Tier 2
    for start, end in tier_2_ranges:
        if start <= pincode_prefix <= end:
            return 'Tier 2'
    
    return 'Tier 3'

def map_utm_source(utm_source):
    """Enhanced UTM source mapping with more platforms and better categorization"""
    if pd.isna(utm_source):
        return 'Direct/Other'
    
    utm_lower = str(utm_source).lower().strip()
    
    # Meta platforms (Facebook, Instagram)
    if any(keyword in utm_lower for keyword in ['facebook', 'fb', 'instagram', 'ig', 'meta', 'insta']):
        return 'Meta (FB/IG)'
    
    # Google platforms
    elif any(keyword in utm_lower for keyword in ['google', 'gdn', 'gsearch', 'adwords', 'youtube', 'yt', 'gmail']):
        return 'Google Ads'
    
    # Twitter/X
    elif any(keyword in utm_lower for keyword in ['twitter', 'x.com', 'tweet']):
        return 'Twitter/X'
    
    # LinkedIn
    elif 'linkedin' in utm_lower or 'lnkd' in utm_lower:
        return 'LinkedIn'
    
    # Snapchat
    elif 'snapchat' in utm_lower or 'snap' in utm_lower:
        return 'Snapchat'
    
    # TikTok
    elif 'tiktok' in utm_lower or 'tik tok' in utm_lower:
        return 'TikTok'
    
    # Pinterest
    elif 'pinterest' in utm_lower or 'pin' in utm_lower:
        return 'Pinterest'
    
    # WhatsApp
    elif 'whatsapp' in utm_lower or 'wa' in utm_lower:
        return 'WhatsApp'
    
    # Email marketing
    elif any(keyword in utm_lower for keyword in ['email', 'mail', 'newsletter', 'mailchimp']):
        return 'Email Marketing'
    
    # Organic/SEO
    elif any(keyword in utm_lower for keyword in ['organic', 'seo', 'search']):
        return 'Organic Search'
    
    # Direct traffic
    elif any(keyword in utm_lower for keyword in ['direct', 'none', '(none)']):
        return 'Direct Traffic'
    
    # Referral
    elif 'referral' in utm_lower or 'ref' in utm_lower:
        return 'Referral'
    
    # Affiliate
    elif 'affiliate' in utm_lower or 'aff' in utm_lower:
        return 'Affiliate'
    
    # Display ads
    elif any(keyword in utm_lower for keyword in ['display', 'banner', 'programmatic']):
        return 'Display Ads'
    
    else:
        return 'Other Sources'

def calculate_payment_success_metrics(df):
    """Calculate comprehensive payment success metrics"""
    total_orders = len(df)
    
    # Success statuses
    success_statuses = ['confirmed', 'delivered', 'shipped', 'processing', 'complete']
    successful_orders = df[df["Status"].str.lower().str.contains('|'.join(success_statuses), na=False)]
    
    # Failed statuses
    failed_statuses = ['cancelled', 'failed', 'rejected', 'abandoned']
    failed_orders = df[df["Status"].str.lower().str.contains('|'.join(failed_statuses), na=False)]
    
    success_count = len(successful_orders)
    failed_count = len(failed_orders)
    
    success_rate = (success_count / total_orders * 100) if total_orders > 0 else 0
    failure_rate = (failed_count / total_orders * 100) if total_orders > 0 else 0
    
    # Payment method wise success
    prepaid_success = len(successful_orders[successful_orders["Payment Type"] == "Prepaid"])
    prepaid_total = len(df[df["Payment Type"] == "Prepaid"])
    prepaid_success_rate = (prepaid_success / prepaid_total * 100) if prepaid_total > 0 else 0
    
    cod_success = len(successful_orders[successful_orders["Payment Type"] == "COD"])
    cod_total = len(df[df["Payment Type"] == "COD"])
    cod_success_rate = (cod_success / cod_total * 100) if cod_total > 0 else 0
    
    return {
        'overall_success_rate': success_rate,
        'overall_failure_rate': failure_rate,
        'prepaid_success_rate': prepaid_success_rate,
        'cod_success_rate': cod_success_rate,
        'successful_orders': success_count,
        'failed_orders': failed_count
    }

# ---------------- HEADER ----------------
st.markdown("""
<div class="dashboard-header">
    <h1>📊 GoKwik Analytics Pro</h1>
    <p>Advanced E-commerce Performance Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### 📁 DATA MANAGEMENT")
    uploaded_file = st.file_uploader(
        "Upload Order Report",
        type=["csv", "xlsx"],
        help="Upload CSV or Excel file with order data"
    )
    
    st.markdown("---")
    
    if uploaded_file:
        st.success("✅ File loaded successfully")

# ---------------- UPLOAD PROCESSING ----------------
if uploaded_file:
    with st.spinner("🔄 Processing data..."):
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

        # Enhanced data cleaning
        df["Order Date"] = pd.to_datetime(df["Created At"], errors="coerce", dayfirst=True)
        df = df[df["Order Date"].notna()]
        
        df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors="coerce")
        df["Status"] = df["Merchant Order Status"]
        df["Payment Method"] = df["Payment Method"].astype(str).str.upper()
        df["Payment Type"] = df["Payment Method"].apply(
            lambda x: "COD" if "COD" in str(x) else "Prepaid"
        )
        
        # Customer ID with better hashing
        if "Customer Phone" in df.columns:
            df["Customer ID"] = df["Customer Phone"].apply(lambda x: str(x).split('|')[0] if pd.notna(x) else "Unknown")
        elif "Customer Name" in df.columns:
            df["Customer ID"] = df["Customer Name"].apply(hash_customer_name)
        
        # Enhanced city tier classification
        if "Billing Pincode" in df.columns:
            df["City Tier"] = df["Billing Pincode"].apply(get_city_tier)
        elif "Shipping Pincode" in df.columns:
            df["City Tier"] = df["Shipping Pincode"].apply(get_city_tier)
        else:
            df["City Tier"] = "Unknown"
        
        # Enhanced UTM source mapping
        if "Utm Source" in df.columns:
            df["UTM Platform"] = df["Utm Source"].apply(map_utm_source)

        save_data(df)
        st.success("✅ Data processed and saved successfully!")

# ---------------- LOAD DATA ----------------
if not uploaded_file:
    df = load_data()
    if df is None:
        st.info("👆 Please upload a file to view the dashboard")
        st.stop()

if "Order Date" not in df.columns:
    st.error("⚠️ Data corrupted. Please re-upload the file.")
    st.stop()

# ---------------- ENHANCED QUICK FILTERS ----------------
if "UTM Platform" in df.columns:
    st.markdown('<div class="section-header">🎯 Quick Platform Filters</div>', unsafe_allow_html=True)
    
    platform_counts = df["UTM Platform"].value_counts().to_dict()
    
    # Platform configuration with icons
    platform_config = {
        'Meta (FB/IG)': '📱',
        'Google Ads': '🔍',
        'Organic Search': '🌱',
        'Email Marketing': '📧',
        'WhatsApp': '💬',
        'Twitter/X': '🐦',
        'LinkedIn': '💼',
        'Direct Traffic': '🔗',
        'Affiliate': '🤝',
        'Display Ads': '🖼️',
        'Other Sources': '🔗'
    }
    
    # Get top 8 platforms
    top_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    
    cols = st.columns(8)
    
    if 'selected_platform' not in st.session_state:
        st.session_state.selected_platform = None
    
    for idx, (platform, count) in enumerate(top_platforms):
        with cols[idx]:
            icon = platform_config.get(platform, '•')
            if st.button(f"{icon} {platform}\n({count:,})", 
                       key=f"btn_{platform}",
                       use_container_width=True):
                st.session_state.selected_platform = platform
                st.rerun()

# ---------------- ENHANCED SIDEBAR FILTERS ----------------
with st.sidebar:
    st.markdown("### 🔍 ADVANCED FILTERS")
    
    valid_dates = df[df["Order Date"].notna()]
    
    if len(valid_dates) == 0:
        st.error("No valid dates found in data")
        st.stop()
    
    min_date = valid_dates["Order Date"].min().date()
    max_date = valid_dates["Order Date"].max().date()
    
    date_range = st.date_input(
        "📅 Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    status_options = df["Status"].unique().tolist()
    status_filter = st.multiselect(
        "📋 Order Status",
        status_options,
        default=status_options
    )
    
    payment_filter = st.multiselect(
        "💳 Payment Type",
        ["Prepaid", "COD"],
        default=["Prepaid", "COD"]
    )
    
    # City Tier filter
    if "City Tier" in df.columns:
        tier_filter = st.multiselect(
            "🏙️ City Tier",
            ["Tier 1", "Tier 2", "Tier 3"],
            default=["Tier 1", "Tier 2", "Tier 3"]
        )
    else:
        tier_filter = []
    
    # Enhanced Platform filter
    if "UTM Platform" in df.columns:
        platforms = sorted(df["UTM Platform"].unique().tolist())
        
        if 'selected_platform' in st.session_state and st.session_state.selected_platform:
            default_platforms = [st.session_state.selected_platform]
        else:
            default_platforms = platforms
        
        platform_filter = st.multiselect(
            "📱 Marketing Platform",
            platforms,
            default=default_platforms
        )
    else:
        platform_filter = []
    
    st.markdown("---")
    
    # Enhanced time granularity
    st.markdown("### 📅 TIME GRANULARITY")
    time_grain = st.radio(
        "Select View Level",
        ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
        index=0,
        horizontal=False
    )
    
    st.markdown("---")
    st.markdown("### 📊 DASHBOARD INFO")
    st.info(f"**Last Updated**\n{datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    
    if st.button("🔄 Reset All Filters"):
        st.session_state.selected_platform = None
        st.rerun()

# ---------------- APPLY FILTERS ----------------
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

# ---------------- ENHANCED KEY METRICS ----------------
st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)

# Calculate metrics
total_orders = filtered["Order Number"].nunique()
total_revenue = filtered["Grand Total"].sum()
avg_order_value = filtered["Grand Total"].mean()
prepaid_orders = filtered[filtered["Payment Type"] == "Prepaid"].shape[0]
cod_orders = filtered[filtered["Payment Type"] == "COD"].shape[0]

# Enhanced payment success metrics
payment_metrics = calculate_payment_success_metrics(filtered)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(create_metric_card("Total Orders", f"{total_orders:,}", icon="🛍️"), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card("Total Revenue", f"₹{total_revenue:,.0f}", icon="💰"), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card("Avg Order Value", f"₹{avg_order_value:,.0f}", icon="💳"), unsafe_allow_html=True)

with col4:
    st.markdown(create_metric_card("Prepaid Orders", f"{prepaid_orders:,}", delta=f"{payment_metrics['prepaid_success_rate']:.1f}% Success", icon="✅"), unsafe_allow_html=True)

with col5:
    st.markdown(create_metric_card("COD Orders", f"{cod_orders:,}", delta=f"{payment_metrics['cod_success_rate']:.1f}% Success", icon="📦"), unsafe_allow_html=True)

with col6:
    st.markdown(create_metric_card("Payment Success", f"{payment_metrics['overall_success_rate']:.1f}%", delta=f"{payment_metrics['failed_orders']} Failed", delta_color="inverse" if payment_metrics['failed_orders'] > 0 else "normal", icon="🎯"), unsafe_allow_html=True)

# ---------------- ENHANCED TRENDS WITH DRILL-DOWN ----------------
st.markdown('<div class="section-header">📊 Revenue & Order Trends Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Enhanced dynamic drill-down
    if time_grain == "Daily":
        trend_data = filtered.groupby(filtered["Order Date"].dt.date).agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        trend_data.columns = ["Date", "Revenue", "Orders"]
        x_data = trend_data["Date"]
        title_text = f"📅 Daily Revenue & Orders ({len(trend_data)} days)"
    elif time_grain == "Weekly":
        filtered_copy = filtered.copy()
        filtered_copy["Week"] = filtered_copy["Order Date"].dt.to_period('W').dt.start_time
        trend_data = filtered_copy.groupby("Week").agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        trend_data.columns = ["Date", "Revenue", "Orders"]
        x_data = trend_data["Date"]
        title_text = f"📅 Weekly Revenue & Orders ({len(trend_data)} weeks)"
    elif time_grain == "Monthly":
        filtered_copy = filtered.copy()
        filtered_copy["Month"] = filtered_copy["Order Date"].dt.to_period('M').dt.start_time
        trend_data = filtered_copy.groupby("Month").agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        trend_data.columns = ["Date", "Revenue", "Orders"]
        x_data = trend_data["Date"]
        title_text = f"📅 Monthly Revenue & Orders ({len(trend_data)} months)"
    elif time_grain == "Quarterly":
        filtered_copy = filtered.copy()
        filtered_copy["Quarter"] = filtered_copy["Order Date"].dt.to_period('Q').dt.start_time
        trend_data = filtered_copy.groupby("Quarter").agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        trend_data.columns = ["Date", "Revenue", "Orders"]
        x_data = trend_data["Date"]
        title_text = f"📅 Quarterly Revenue & Orders ({len(trend_data)} quarters)"
    else:  # Yearly
        filtered_copy = filtered.copy()
        filtered_copy["Year"] = filtered_copy["Order Date"].dt.year
        trend_data = filtered_copy.groupby("Year").agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        trend_data.columns = ["Date", "Revenue", "Orders"]
        x_data = trend_data["Date"]
        title_text = f"📅 Yearly Revenue & Orders ({len(trend_data)} years)"
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=x_data, 
            y=trend_data["Revenue"],
            name="Revenue",
            line=dict(color='#667eea', width=4),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.15)',
            mode='lines+markers',
            marker=dict(size=8, symbol='circle')
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=x_data, 
            y=trend_data["Orders"],
            name="Orders",
            line=dict(color='#f093fb', width=3, dash='dot'),
            mode='lines+markers',
            marker=dict(size=6, symbol='diamond')
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=18, color='#1e293b', family="Inter")),
        height=450,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter", size=12, color='#1e293b'),
        margin=dict(l=70, r=70, t=70, b=70),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#667eea",
            borderwidth=1
        )
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0', tickfont=dict(color='#1e293b'))
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0', secondary_y=False, title="Revenue (₹)", tickfont=dict(color='#1e293b'))
    fig.update_yaxes(showgrid=False, secondary_y=True, title="Orders", tickfont=dict(color='#1e293b'))
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Enhanced payment split
    payment_split = filtered.groupby("Payment Type").agg({
        "Order Number": "count",
        "Grand Total": "sum"
    }).reset_index()
    
    fig = go.Figure(data=[go.Pie(
        labels=payment_split["Payment Type"],
        values=payment_split["Order Number"],
        hole=0.6,
        marker=dict(colors=['#667eea', '#f093fb']),
        textinfo='label+percent',
        textfont_size=16,
        textfont_color='white',
        textposition='inside',
        pull=[0.1, 0]
    )])
    
    # Add center annotation
    total_payment_orders = payment_split["Order Number"].sum()
    fig.add_annotation(
        text=f"<b>{total_payment_orders:,}</b><br>Total<br>Orders",
        x=0.5, y=0.5,
        font_size=18,
        showarrow=False,
        font_color='#1e293b'
    )
    
    fig.update_layout(
        title=dict(text="💳 Payment Method Split", font=dict(size=18, color='#1e293b', family="Inter")),
        height=450,
        showlegend=True,
        paper_bgcolor='white',
        font=dict(family="Inter", size=14, color='#1e293b'),
        margin=dict(l=20, r=20, t=70, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------- GEOGRAPHIC & TIER ANALYSIS ----------------
st.markdown('<div class="section-header">🗺️ Geographic Distribution & City Tier Performance</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Enhanced state-wise analysis
    if "Billing State" in filtered.columns:
        state_data = filtered.groupby("Billing State").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        state_data.columns = ["State", "Orders", "Revenue"]
        state_data["AOV"] = state_data["Revenue"] / state_data["Orders"]
        state_data = state_data.sort_values("Orders", ascending=False).head(15)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=state_data["State"],
            y=state_data["Orders"],
            name="Orders",
            marker=dict(
                color=state_data["Revenue"],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Revenue (₹)", x=1.15)
            ),
            text=state_data["Orders"],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<br>Revenue: ₹%{marker.color:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text="🏆 Top 15 States by Order Volume", font=dict(size=18, color='#1e293b')),
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, title="State", tickangle=-45, tickfont=dict(color='#1e293b', size=10)),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders", tickfont=dict(color='#1e293b')),
            font=dict(family="Inter", size=12, color='#1e293b'),
            margin=dict(l=70, r=130, t=70, b=100)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Enhanced city tier analysis
    if "City Tier" in filtered.columns:
        tier_data = filtered.groupby("City Tier").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        tier_data.columns = ["Tier", "Orders", "Revenue"]
        tier_data["AOV"] = tier_data["Revenue"] / tier_data["Orders"]
        
        tier_order = ["Tier 1", "Tier 2", "Tier 3"]
        tier_data["Tier"] = pd.Categorical(tier_data["Tier"], categories=tier_order, ordered=True)
        tier_data = tier_data.sort_values("Tier")
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=tier_data["Tier"],
                y=tier_data["Orders"],
                name="Orders",
                marker=dict(
                    color=['#667eea', '#764ba2', '#f093fb'],
                    line=dict(color='white', width=2)
                ),
                text=tier_data["Orders"],
                textposition='outside'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=tier_data["Tier"],
                y=tier_data["AOV"],
                name="AOV",
                mode='lines+markers',
                marker=dict(color='#fee140', size=14, symbol='diamond'),
                line=dict(color='#fee140', width=4)
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title=dict(text="🏙️ City Tier Performance Analysis", font=dict(size=18, color='#1e293b')),
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, title="City Tier", tickfont=dict(color='#1e293b')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders", tickfont=dict(color='#1e293b')),
            yaxis2=dict(showgrid=False, overlaying='y', side='right', title="AOV (₹)", tickfont=dict(color='#1e293b')),
            font=dict(family="Inter", size=12, color='#1e293b'),
            margin=dict(l=70, r=70, t=70, b=70),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- MARKETING PERFORMANCE ----------------
st.markdown('<div class="section-header">📱 Marketing Channel Performance & Attribution</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Enhanced platform analysis
    if "UTM Platform" in filtered.columns:
        platform_data = filtered.groupby("UTM Platform").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        platform_data.columns = ["Platform", "Orders", "Revenue"]
        platform_data["AOV"] = platform_data["Revenue"] / platform_data["Orders"]
        platform_data = platform_data.sort_values("Orders", ascending=False)
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=platform_data["Platform"],
                y=platform_data["Orders"],
                name="Orders",
                marker=dict(color='#667eea'),
                text=platform_data["Orders"],
                textposition='outside'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=platform_data["Platform"],
                y=platform_data["AOV"],
                name="AOV",
                mode='lines+markers',
                marker=dict(color='#f093fb', size=12),
                line=dict(color='#f093fb', width=4)
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title=dict(text="📊 Platform Performance: Orders & AOV", font=dict(size=18, color='#1e293b')),
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, title="Platform", tickangle=-45, tickfont=dict(color='#1e293b', size=10)),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders", tickfont=dict(color='#1e293b')),
            yaxis2=dict(showgrid=False, overlaying='y', side='right', title="AOV (₹)", tickfont=dict(color='#1e293b')),
            font=dict(family="Inter", size=11, color='#1e293b'),
            margin=dict(l=70, r=70, t=70, b=120),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Platform revenue share
    if "UTM Platform" in filtered.columns:
        platform_revenue = filtered.groupby("UTM Platform")["Grand Total"].sum().reset_index()
        platform_revenue.columns = ["Platform", "Revenue"]
        platform_revenue = platform_revenue.sort_values("Revenue", ascending=False)
        
        fig = go.Figure(data=[go.Pie(
            labels=platform_revenue["Platform"],
            values=platform_revenue["Revenue"],
            hole=0.5,
            marker=dict(
                colors=px.colors.qualitative.Set3,
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textfont_size=12,
            textposition='auto'
        )])
        
        total_platform_revenue = platform_revenue["Revenue"].sum()
        fig.add_annotation(
            text=f"<b>₹{total_platform_revenue/1000:.1f}K</b><br>Total<br>Revenue",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False,
            font_color='#1e293b'
        )
        
        fig.update_layout(
            title=dict(text="💰 Revenue Distribution by Platform", font=dict(size=18, color='#1e293b')),
            height=450,
            showlegend=True,
            paper_bgcolor='white',
            font=dict(family="Inter", size=11, color='#1e293b'),
            margin=dict(l=20, r=20, t=70, b=20),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- RFM ANALYSIS ----------------
st.markdown('<div class="section-header">🎯 Customer Segmentation - RFM Analysis</div>', unsafe_allow_html=True)

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
            labels = list(range(1, n_bins + 1)) if ascending else list(range(n_bins, 0, -1))
            
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
                return pd.cut(ranks, bins=5, labels=[1, 2, 3, 4, 5] if ascending else [5, 4, 3, 2, 1])
    
    rfm_data["R_Score"] = calculate_score(rfm_data, "Recency", ascending=False)
    rfm_data["F_Score"] = calculate_score(rfm_data, "Frequency", ascending=True)
    rfm_data["M_Score"] = calculate_score(rfm_data, "Monetary", ascending=True)
    
    rfm_data["RFM_Total"] = rfm_data["R_Score"].astype(int) + rfm_data["F_Score"].astype(int) + rfm_data["M_Score"].astype(int)
    
    def segment_customer(score):
        if score >= 13:
            return "🌟 Champions"
        elif score >= 11:
            return "💎 Loyal Customers"
        elif score >= 9:
            return "🎯 Potential Loyalists"
        elif score >= 7:
            return "⚠️ At Risk"
        else:
            return "😔 Lost Customers"
    
    rfm_data["Segment"] = rfm_data["RFM_Total"].apply(segment_customer)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        segment_counts = rfm_data["Segment"].value_counts().reset_index()
        segment_counts.columns = ["Segment", "Customers"]
        
        color_map = {
            "🌟 Champions": "#10b981",
            "💎 Loyal Customers": "#3b82f6",
            "🎯 Potential Loyalists": "#f59e0b",
            "⚠️ At Risk": "#f97316",
            "😔 Lost Customers": "#ef4444"
        }
        
        colors = [color_map.get(seg, "#667eea") for seg in segment_counts["Segment"]]
        
        fig = go.Figure(data=[go.Bar(
            x=segment_counts["Segment"],
            y=segment_counts["Customers"],
            marker=dict(color=colors, line=dict(color='white', width=2)),
            text=segment_counts["Customers"],
            textposition='outside'
        )])
        
        fig.update_layout(
            title=dict(text="👥 Customer Segments", font=dict(size=16, color='#1e293b')),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickangle=-20, tickfont=dict(color='#1e293b', size=10)),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Customers", tickfont=dict(color='#1e293b')),
            font=dict(family="Inter", size=11, color='#1e293b'),
            margin=dict(l=60, r=60, t=60, b=100)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(data=[go.Histogram(
            x=rfm_data["Recency"],
            nbinsx=40,
            marker=dict(
                color='#667eea',
                line=dict(color='white', width=1)
            )
        )])
        
        fig.update_layout(
            title=dict(text="📅 Recency Distribution", font=dict(size=16, color='#1e293b')),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(title="Days Since Last Order", tickfont=dict(color='#1e293b')),
            yaxis=dict(title="Customers", tickfont=dict(color='#1e293b')),
            font=dict(family="Inter", size=11, color='#1e293b'),
            margin=dict(l=60, r=60, t=60, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=rfm_data["Frequency"],
            y=rfm_data["Monetary"],
            mode='markers',
            marker=dict(
                size=rfm_data["RFM_Total"] * 2.5,
                color=rfm_data["RFM_Total"],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="RFM Score"),
                line=dict(color='white', width=1),
                opacity=0.7
            ),
            hovertemplate='<b>Customer</b><br>Orders: %{x}<br>Revenue: ₹%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text="💰 Frequency vs Monetary", font=dict(size=16, color='#1e293b')),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Frequency", tickfont=dict(color='#1e293b')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Monetary (₹)", tickfont=dict(color='#1e293b')),
            font=dict(family="Inter", size=11, color='#1e293b'),
            margin=dict(l=60, r=60, t=60, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- DATA TABLE ----------------
st.markdown('<div class="section-header">📋 Detailed Order Records</div>', unsafe_allow_html=True)

display_cols = [
    "Order Number", "Order Date", "Status", "Payment Method", 
    "Grand Total", "Customer ID", "Billing State", "Billing City", 
    "Billing Pincode", "City Tier", "Product Name", "UTM Platform", "Utm Source"
]
display_cols = [col for col in display_cols if col in filtered.columns]

st.dataframe(
    filtered[display_cols].head(1000).style.format({
        "Grand Total": "₹{:,.0f}",
        "Order Date": lambda x: x.strftime("%d %b %Y") if pd.notnull(x) else ""
    }),
    use_container_width=True,
    height=450
)

# ---------------- EXPORT ----------------
st.markdown('<div class="section-header">⬇️ Export Analytics Data</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    st.download_button(
        "📥 Download CSV",
        filtered.drop(columns=["__last_updated__"], errors='ignore').to_csv(index=False),
        file_name=f"gokwik_analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    st.download_button(
        "📊 Download Excel",
        filtered.drop(columns=["__last_updated__"], errors='ignore').to_csv(index=False),
        file_name=f"gokwik_analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 25px; font-family: Inter;">
    <p style="font-size: 14px; font-weight: 600;">GoKwik Analytics Pro Dashboard</p>
    <p style="font-size: 12px; margin-top: 5px;">Powered by Streamlit & Plotly | Advanced E-commerce Intelligence</p>
</div>
""", unsafe_allow_html=True)
