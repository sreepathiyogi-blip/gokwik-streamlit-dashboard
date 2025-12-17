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
        font-size: 22px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 35px 0 20px 0;
        padding: 18px 20px;
        border-left: 5px solid #667eea;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
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
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
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
    """Load data from Parquet or CSV fallback"""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_parquet(DATA_FILE)
            # Ensure Order Date is datetime
            if "Order Date" in df.columns:
                df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
            return df
        except Exception:
            # Try CSV fallback
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
    
    # Convert categorical columns to string to avoid PyArrow issues
    for col in df.columns:
        if df[col].dtype.name == 'category':
            df[col] = df[col].astype(str)
        # Convert object columns to string (except datetime)
        elif df[col].dtype == 'object' and col != 'Order Date':
            df[col] = df[col].astype(str)
    
    # Ensure datetime columns are proper datetime type
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
    
    try:
        df.to_parquet(DATA_FILE, index=False, engine='pyarrow')
    except Exception as e:
        # Fallback: save as CSV if Parquet fails
        csv_file = DATA_FILE.replace('.parquet', '.csv')
        df.to_csv(csv_file, index=False)
        st.warning(f"⚠️ Saved as CSV instead of Parquet due to compatibility issue.")

def read_file(file):
    """Read CSV or Excel file"""
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file, encoding='utf-8')
        else:
            return pd.read_excel(file)
    except UnicodeDecodeError:
        # Try different encoding if UTF-8 fails
        return pd.read_csv(file, encoding='latin-1')

def hash_customer_name(name):
    """Hash customer name for privacy"""
    if pd.isna(name):
        return "Unknown"
    return hashlib.md5(str(name).encode()).hexdigest()[:8]

def create_metric_card(label, value, delta=None, delta_color="normal"):
    """Create HTML metric card"""
    delta_html = f'<div style="color: {"#10b981" if delta_color == "normal" else "#ef4444"}; font-size: 14px; font-weight: 600; margin-top: 8px;">{delta}</div>' if delta else ""
    
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

        # Data cleaning - handle multiple date formats
        df["Order Date"] = pd.to_datetime(df["Created At"], errors="coerce", dayfirst=True)
        
        # Remove rows with invalid dates
        initial_count = len(df)
        df = df[df["Order Date"].notna()].copy()
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            st.warning(f"⚠️ Removed {removed_count} rows with invalid dates")
        
        if len(df) == 0:
            st.error("❌ No valid data after date processing. Please check your file.")
            st.stop()
        
        # Clean numeric data
        df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors="coerce").fillna(0)
        
        # Clean status and payment data
        df["Status"] = df["Merchant Order Status"].astype(str)
        df["Payment Method"] = df["Payment Method"].astype(str).str.upper()
        df["Payment Type"] = df["Payment Method"].apply(
            lambda x: "COD" if "COD" in str(x) else "Prepaid"
        )
        
        # Hash customer names for privacy
        if "Customer Name" in df.columns:
            df["Customer ID"] = df["Customer Name"].apply(hash_customer_name)
        
        # Add city tier classification
        if "Billing State" in df.columns:
            df["City Tier"] = df["Billing State"].apply(get_city_tier)

        save_data(df)
        
        with st.sidebar:
            st.success(f"✅ Successfully loaded {len(df):,} orders")
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.stop()

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
    
    # Ensure valid dates exist
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
    
    # Campaign filter
    if "Utm Campaign" in df.columns:
        campaigns = df["Utm Campaign"].dropna().unique().tolist()
        if campaigns and len(campaigns) < 50:
            campaign_filter = st.multiselect(
                "Campaign",
                campaigns,
                default=campaigns[:10] if len(campaigns) > 10 else campaigns
            )
        else:
            campaign_filter = campaigns if campaigns else []
    else:
        campaign_filter = []
    
    st.markdown("---")
    
    # Drill-down level selector
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
try:
    filtered = df[
        (df["Order Date"].dt.date >= date_range[0]) &
        (df["Order Date"].dt.date <= date_range[1]) &
        (df["Status"].isin(status_filter)) &
        (df["Payment Type"].isin(payment_filter))
    ].copy()

    # Apply City Tier filter
    if tier_filter and "City Tier" in filtered.columns:
        filtered = filtered[filtered["City Tier"].isin(tier_filter)]

    # Apply UTM filters if available
    if utm_filter and "Utm Source" in filtered.columns:
        filtered = filtered[filtered["Utm Source"].isin(utm_filter)]

    if campaign_filter and "Utm Campaign" in filtered.columns:
        filtered = filtered[filtered["Utm Campaign"].isin(campaign_filter)]

    if len(filtered) == 0:
        st.warning("⚠️ No data matches the selected filters. Please adjust your filters.")
        st.stop()

except Exception as e:
    st.error(f"Error applying filters: {str(e)}")
    st.stop()

# ---------------- KEY METRICS ----------------
st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

total_orders = filtered["Order Number"].nunique()
total_revenue = filtered["Grand Total"].sum()
avg_order_value = filtered["Grand Total"].mean() if len(filtered) > 0 else 0
prepaid_orders = filtered[filtered["Payment Type"] == "Prepaid"].shape[0]
cod_orders = filtered[filtered["Payment Type"] == "COD"].shape[0]

# Calculate Payment Success Ratio
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
    # Dynamic revenue and orders trend based on time granularity
    if time_grain == "Daily":
        daily = filtered.groupby(filtered["Order Date"].dt.date).agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        daily.columns = ["Date", "Revenue", "Orders"]
        x_data = daily["Date"]
        title_text = "Daily Revenue & Orders"
    elif time_grain == "Weekly":
        filtered_copy = filtered.copy()
        filtered_copy["Week"] = filtered_copy["Order Date"].dt.to_period('W').dt.start_time
        daily = filtered_copy.groupby("Week").agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        daily.columns = ["Date", "Revenue", "Orders"]
        x_data = daily["Date"]
        title_text = "Weekly Revenue & Orders"
    elif time_grain == "Monthly":
        filtered_copy = filtered.copy()
        filtered_copy["Month"] = filtered_copy["Order Date"].dt.to_period('M').dt.start_time
        daily = filtered_copy.groupby("Month").agg({
            "Grand Total": "sum",
            "Order Number": "count"
        }).reset_index()
        daily.columns = ["Date", "Revenue", "Orders"]
        x_data = daily["Date"]
        title_text = "Monthly Revenue & Orders"
    else:  # Yearly
        filtered_copy = filtered.copy()
        filtered_copy["Year"] = filtered_copy["Order Date"].dt.year
        daily = filtered_copy.groupby("Year").agg({
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
    # Payment method split
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

col1, col2 = st.columns(2)

with col1:
    # India Map with state-wise orders
    if "Billing State" in filtered.columns:
        state_data = filtered.groupby("Billing State").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        state_data.columns = ["State", "Orders", "Revenue"]
        
        # Create choropleth map
        fig = go.Figure(data=go.Choropleth(
            locationmode='country names',
            locations=state_data["State"],
            z=state_data["Orders"],
            text=state_data["State"],
            colorscale='Blues',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title="Orders",
            hovertemplate='<b>%{text}</b><br>Orders: %{z:,}<extra></extra>'
        ))
        
        fig.update_geos(
            visible=False,
            resolution=50,
            showcountries=False,
            showcoastlines=False,
            showland=False,
            fitbounds="locations"
        )
        
        fig.update_layout(
            title=dict(text="State-wise Order Distribution", font=dict(size=16, color='#1a1a1a')),
            height=400,
            geo=dict(
                bgcolor='white',
                lakecolor='white',
                landcolor='#f0f0f0'
            ),
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # City Tier Analysis
    if "City Tier" in filtered.columns:
        tier_data = filtered.groupby("City Tier").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        tier_data.columns = ["Tier", "Orders", "Revenue"]
        tier_data["AOV"] = tier_data["Revenue"] / tier_data["Orders"]
        
        # Sort by tier
        tier_order = ["Tier 1", "Tier 2", "Tier 3"]
        tier_data["Tier"] = pd.Categorical(tier_data["Tier"], categories=tier_order, ordered=True)
        tier_data = tier_data.sort_values("Tier")
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=tier_data["Tier"],
                y=tier_data["Orders"],
                name="Orders",
                marker=dict(color=['#667eea', '#764ba2', '#f093fb']),
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
                marker=dict(color='#fee140', size=12),
                line=dict(color='#fee140', width=3)
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title=dict(text="City Tier Performance", font=dict(size=16, color='#1a1a1a')),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, title="City Tier", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            yaxis2=dict(showgrid=False, overlaying='y', side='right', title="AOV (₹)", tickfont=dict(color='#1a1a1a'), title_font=dict(color='#1a1a1a')),
            font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
            margin=dict(l=60, r=60, t=60, b=60),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#1a1a1a'))
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
            text_data = state_data["Revenue"].apply(lambda x: f"₹{x:,.0f}")
        
        fig = go.Figure(data=[go.Bar(
            x=y_data,
            y=state_data["State"],
            orientation='h',
            marker=dict(
                color=color_data,
                colorscale='Blues' if top10_metric == "Orders" else 'Greens',
                showscale=False
            ),
            text=text_data,
            textposition='auto'
        )])
        
        fig.update_layout(
            title=dict(text=title_text, font=dict(size=16, color='#1a1a1a')),
            height=500,
            xaxis_title=top10_metric,
            yaxis_title="State",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
            margin=dict(l=150, r=60, t=60, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- PAYMENT SUCCESS RATIO ----------------
st.markdown('<div class="section-header">💳 Payment Performance</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

confirmed_orders = filtered[filtered["Status"].str.contains("Confirmed|Delivered|Shipped", case=False, na=False)].shape[0]
total_attempts = filtered.shape[0]
success_ratio = (confirmed_orders / total_attempts * 100) if total_attempts > 0 else 0

prepaid_confirmed = filtered[(filtered["Payment Type"] == "Prepaid") & 
                                (filtered["Status"].str.contains("Confirmed|Delivered|Shipped", case=False, na=False))].shape[0]
prepaid_total = filtered[filtered["Payment Type"] == "Prepaid"].shape[0]
prepaid_success = (prepaid_confirmed / prepaid_total * 100) if prepaid_total > 0 else 0

cod_confirmed = filtered[(filtered["Payment Type"] == "COD") & 
                            (filtered["Status"].str.contains("Confirmed|Delivered|Shipped", case=False, na=False))].shape[0]
cod_total = filtered[filtered["Payment Type"] == "COD"].shape[0]
cod_success = (cod_confirmed / cod_total * 100) if cod_total > 0 else 0

with col1:
    st.markdown(create_metric_card("Overall Success Rate", f"{success_ratio:.1f}%", 
                                    f"{confirmed_orders:,} / {total_attempts:,} orders"), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card("Prepaid Success Rate", f"{prepaid_success:.1f}%",
                                    f"{prepaid_confirmed:,} / {prepaid_total:,} orders"), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card("COD Success Rate", f"{cod_success:.1f}%",
                                    f"{cod_confirmed:,} / {cod_total:,} orders"), unsafe_allow_html=True)

    # ---------------- TIME GRANULARITY ANALYSIS ----------------
    st.markdown('<div class="section-header">📅 Time-Based Analysis</div>', unsafe_allow_html=True)
    
    time_granularity = st.radio(
        "Select Time Granularity:",
        ["Daily", "Weekly", "Monthly", "Yearly"],
        horizontal=True
    )
    
    # Prepare time-based data
    time_df = filtered.copy()
    
    if time_granularity == "Daily":
        time_df["Period"] = time_df["Order Date"].dt.date
        title_suffix = "Daily"
    elif time_granularity == "Weekly":
        time_df["Period"] = time_df["Order Date"].dt.to_period("W").apply(lambda x: x.start_time)
        title_suffix = "Weekly"
    elif time_granularity == "Monthly":
        time_df["Period"] = time_df["Order Date"].dt.to_period("M").apply(lambda x: x.start_time)
        title_suffix = "Monthly"
    else:  # Yearly
        time_df["Period"] = time_df["Order Date"].dt.to_period("Y").apply(lambda x: x.start_time)
        title_suffix = "Yearly"
    
    time_summary = time_df.groupby("Period").agg({
        "Order Number": "count",
        "Grand Total": "sum"
    }).reset_index()
    time_summary.columns = ["Period", "Orders", "Revenue"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_orders = px.line(time_summary, x="Period", y="Orders",
                            title=f"{title_suffix} Orders Trend",
                            markers=True)
        fig_orders.update_traces(line_color="#667eea", line_width=3)
        fig_orders.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=400
        )
        st.plotly_chart(fig_orders, use_container_width=True)
    
    with col2:
        fig_revenue = px.line(time_summary, x="Period", y="Revenue",
                             title=f"{title_suffix} Revenue Trend",
                             markers=True)
        fig_revenue.update_traces(line_color="#10b981", line_width=3)
        fig_revenue.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=400
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # ---------------- CITY TIER ANALYSIS ----------------
    st.markdown('<div class="section-header">🏙️ City Tier Analysis</div>', unsafe_allow_html=True)
    
    # Define city tiers (you can customize this list)
    tier1_cities = ["Mumbai", "Delhi", "Bangalore", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad"]
    tier2_cities = ["Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", 
                   "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", 
                   "Kalyan-Dombivali", "Vasai-Virar", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar"]
    
    if "Shipping City" in filtered.columns:
        city_data = filtered.copy()
        city_data["City"] = city_data["Shipping City"].str.strip().str.title()
        
        def classify_tier(city):
            if pd.isna(city):
                return "Unknown"
            elif city in tier1_cities:
                return "Tier 1"
            elif city in tier2_cities:
                return "Tier 2"
            else:
                return "Tier 3"
        
        city_data["City Tier"] = city_data["City"].apply(classify_tier)
        
        tier_summary = city_data.groupby("City Tier").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        tier_summary.columns = ["Tier", "Orders", "Revenue"]
        tier_summary["AOV"] = tier_summary["Revenue"] / tier_summary["Orders"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_tier_orders = px.pie(tier_summary, values="Orders", names="Tier",
                                    title="Orders by City Tier",
                                    color_discrete_sequence=px.colors.qualitative.Set3)
            fig_tier_orders.update_layout(height=350)
            st.plotly_chart(fig_tier_orders, use_container_width=True)
        
        with col2:
            fig_tier_revenue = px.pie(tier_summary, values="Revenue", names="Tier",
                                     title="Revenue by City Tier",
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_tier_revenue.update_layout(height=350)
            st.plotly_chart(fig_tier_revenue, use_container_width=True)
        
        with col3:
            fig_tier_aov = px.bar(tier_summary, x="Tier", y="AOV",
                                 title="AOV by City Tier",
                                 color="AOV",
                                 color_continuous_scale="Blues")
            fig_tier_aov.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_tier_aov, use_container_width=True)
        
        # Detailed tier breakdown
        st.dataframe(tier_summary.style.format({
            "Orders": "{:,.0f}",
            "Revenue": "₹{:,.0f}",
            "AOV": "₹{:,.0f}"
        }), use_container_width=True)
    
    # ---------------- INDIA MAP VISUALIZATION ----------------
    st.markdown('<div class="section-header">🗺️ Geographic Distribution</div>', unsafe_allow_html=True)
    
    if "Shipping State" in filtered.columns:
        state_data = filtered.groupby("Shipping State").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        state_data.columns = ["State", "Orders", "Revenue"]
        state_data = state_data.sort_values("Revenue", ascending=False)
        
        # State code mapping for map
        state_codes = {
            "Andhra Pradesh": "AP", "Arunachal Pradesh": "AR", "Assam": "AS", "Bihar": "BR",
            "Chhattisgarh": "CT", "Goa": "GA", "Gujarat": "GJ", "Haryana": "HR", "Himachal Pradesh": "HP",
            "Jharkhand": "JH", "Karnataka": "KA", "Kerala": "KL", "Madhya Pradesh": "MP", "Maharashtra": "MH",
            "Manipur": "MN", "Meghalaya": "ML", "Mizoram": "MZ", "Nagaland": "NL", "Odisha": "OR",
            "Punjab": "PB", "Rajasthan": "RJ", "Sikkim": "SK", "Tamil Nadu": "TN", "Telangana": "TG",
            "Tripura": "TR", "Uttar Pradesh": "UP", "Uttarakhand": "UT", "West Bengal": "WB",
            "Delhi": "DL", "Jammu and Kashmir": "JK", "Ladakh": "LA"
        }
        
        state_data["Code"] = state_data["State"].map(state_codes)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_map_orders = px.choropleth(
                state_data,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM',
                locations='State',
                color='Orders',
                color_continuous_scale="Blues",
                title="Orders by State"
            )
            fig_map_orders.update_geos(fitbounds="locations", visible=False)
            fig_map_orders.update_layout(height=500)
            st.plotly_chart(fig_map_orders, use_container_width=True)
        
        with col2:
            fig_map_revenue = px.choropleth(
                state_data,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM',
                locations='State',
                color='Revenue',
                color_continuous_scale="Greens",
                title="Revenue by State"
            )
            fig_map_revenue.update_geos(fitbounds="locations", visible=False)
            fig_map_revenue.update_layout(height=500)
            st.plotly_chart(fig_map_revenue, use_container_width=True)
    
    # ---------------- TOP 10 TOGGLE ----------------
    st.markdown('<div class="section-header">🏆 Top Performers</div>', unsafe_allow_html=True)
    
    top_metric = st.radio("View Top 10 by:", ["Orders", "Revenue"], horizontal=True)
    
    if "Shipping City" in filtered.columns:
        if top_metric == "Orders":
            top_cities = filtered.groupby("Shipping City").agg({
                "Order Number": "count"
            }).reset_index()
            top_cities.columns = ["City", "Orders"]
            top_cities = top_cities.sort_values("Orders", ascending=False).head(10)
            
            fig_top = px.bar(top_cities, x="Orders", y="City", orientation="h",
                           title="Top 10 Cities by Orders",
                           color="Orders",
                           color_continuous_scale="Blues")
        else:
            top_cities = filtered.groupby("Shipping City").agg({
                "Grand Total": "sum"
            }).reset_index()
            top_cities.columns = ["City", "Revenue"]
            top_cities = top_cities.sort_values("Revenue", ascending=False).head(10)
            
            fig_top = px.bar(top_cities, x="Revenue", y="City", orientation="h",
                           title="Top 10 Cities by Revenue",
                           color="Revenue",
                           color_continuous_scale="Greens")
        
        fig_top.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)
    
    # ---------------- RFM ANALYSIS ----------------
    st.markdown('<div class="section-header">👥 RFM Customer Analysis</div>', unsafe_allow_html=True)
    
    if "Customer Phone" in filtered.columns or "Shipping Phone" in filtered.columns:
        import hashlib
        
        # Use phone as customer identifier
        phone_col = "Customer Phone" if "Customer Phone" in filtered.columns else "Shipping Phone"
        customer_col = "Customer Name" if "Customer Name" in filtered.columns else "Shipping Name"
        
        rfm_data = filtered[[phone_col, customer_col, "Order Date", "Grand Total"]].copy()
        rfm_data.columns = ["Phone", "Name", "OrderDate", "Revenue"]
        
        # Hash phone numbers for privacy
        rfm_data["CustomerID"] = rfm_data["Phone"].apply(
            lambda x: hashlib.md5(str(x).encode()).hexdigest()[:8] if pd.notna(x) else "Unknown"
        )
        
        # Hash names for privacy
        rfm_data["HashedName"] = rfm_data["Name"].apply(
            lambda x: hashlib.md5(str(x).encode()).hexdigest()[:8] if pd.notna(x) else "Unknown"
        )
        
        # Calculate RFM metrics
        analysis_date = filtered["Order Date"].max()
        
        rfm = rfm_data.groupby("CustomerID").agg({
            "OrderDate": lambda x: (analysis_date - x.max()).days,  # Recency
            "Phone": "count",  # Frequency
            "Revenue": "sum",  # Monetary
            "HashedName": "first"  # Get hashed name
        }).reset_index()
        
        rfm.columns = ["CustomerID", "Recency", "Frequency", "Monetary", "HashedName"]
        
        # RFM Scoring (1-5 scale) with safe binning
        try:
            rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        except ValueError:
            rfm["R_Score"] = pd.cut(rfm["Recency"], bins=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        
        try:
            rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        except ValueError:
            rfm["F_Score"] = pd.cut(rfm["Frequency"], bins=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        
        try:
            rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        except ValueError:
            rfm["M_Score"] = pd.cut(rfm["Monetary"], bins=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        
        rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
        
        # Customer Segments
        def segment_customer(row):
            score = int(row["R_Score"]) + int(row["F_Score"]) + int(row["M_Score"])
            if score >= 13:
                return "Champions"
            elif score >= 11:
                return "Loyal Customers"
            elif score >= 9:
                return "Potential Loyalists"
            elif score >= 7:
                return "At Risk"
            else:
                return "Lost"
        
        rfm["Segment"] = rfm.apply(segment_customer, axis=1)
        
        # Segment summary
        segment_summary = rfm.groupby("Segment").agg({
            "CustomerID": "count",
            "Monetary": "sum"
        }).reset_index()
        segment_summary.columns = ["Segment", "Customers", "Total Revenue"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_segments = px.pie(segment_summary, values="Customers", names="Segment",
                                title="Customer Segmentation",
                                color_discrete_sequence=px.colors.qualitative.Set3)
            fig_segments.update_layout(height=400)
            st.plotly_chart(fig_segments, use_container_width=True)
        
        with col2:
            fig_segment_revenue = px.bar(segment_summary, x="Segment", y="Total Revenue",
                                        title="Revenue by Customer Segment",
                                        color="Total Revenue",
                                        color_continuous_scale="Viridis")
            fig_segment_revenue.update_layout(height=400)
            st.plotly_chart(fig_segment_revenue, use_container_width=True)
        
        # Top 15 Customers with hashed names
        st.markdown("### 🌟 Top 15 Customers (By Revenue)")
        top_customers = rfm.nlargest(15, "Monetary")[["HashedName", "Recency", "Frequency", "Monetary", "Segment"]]
        top_customers.columns = ["Customer ID", "Days Since Last Order", "Total Orders", "Total Spent", "Segment"]
        
        st.dataframe(top_customers.style.format({
            "Days Since Last Order": "{:.0f}",
            "Total Orders": "{:.0f}",
            "Total Spent": "₹{:,.0f}"
        }).background_gradient(subset=["Total Spent"], cmap="Greens"), use_container_width=True)
        
        # RFM Distribution
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_recency = px.histogram(rfm, x="Recency", nbins=30,
                                      title="Recency Distribution",
                                      color_discrete_sequence=["#667eea"])
            fig_recency.update_layout(height=300)
            st.plotly_chart(fig_recency, use_container_width=True)
        
        with col2:
            fig_frequency = px.histogram(rfm, x="Frequency", nbins=20,
                                        title="Frequency Distribution",
                                        color_discrete_sequence=["#10b981"])
            fig_frequency.update_layout(height=300)
            st.plotly_chart(fig_frequency, use_container_width=True)
        
        with col3:
            fig_monetary = px.histogram(rfm, x="Monetary", nbins=30,
                                       title="Monetary Distribution",
                                       color_discrete_sequence=["#f59e0b"])
            fig_monetary.update_layout(height=300)
            st.plotly_chart(fig_monetary, use_container_width=True)
            
