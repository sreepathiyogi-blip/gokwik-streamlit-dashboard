import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import date, datetime

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
        background: #f5f7fa;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 10px 0;
    }
    
    /* Metric value */
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 10px 0;
    }
    
    /* Metric label */
    .metric-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
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
        font-size: 20px;
        font-weight: 600;
        color: #1a1a1a;
        margin: 25px 0 15px 0;
        padding-left: 10px;
        border-left: 4px solid #667eea;
        background: white;
        padding: 15px;
        border-radius: 8px;
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
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
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

def create_metric_card(label, value, delta=None, delta_color="normal"):
    delta_html = f'<div style="color: {"green" if delta_color == "normal" else "red"}; font-size: 14px;">{delta}</div>' if delta else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-label" style="color: #666; font-weight: 600;">{label}</div>
        <div class="metric-value" style="color: #1a1a1a; font-weight: 700;">{value}</div>
        {delta_html}
    </div>
    """

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

    # Data cleaning - handle multiple date formats
    df["Order Date"] = pd.to_datetime(df["Created At"], errors="coerce", dayfirst=True)
    
    # Remove rows with invalid dates
    df = df[df["Order Date"].notna()]
    
    df["Grand Total"] = pd.to_numeric(df["Grand Total"], errors="coerce")
    df["Status"] = df["Merchant Order Status"]
    df["Payment Method"] = df["Payment Method"].astype(str).str.upper()
    df["Payment Type"] = df["Payment Method"].apply(
        lambda x: "COD" if "COD" in str(x) else "Prepaid"
    )

    save_data(df)
    with st.sidebar:
        st.success("✅ File uploaded successfully")

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
    st.markdown("### 📊 Dashboard Info")
    st.info(f"**Last Updated:** {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

# ---------------- APPLY FILTERS ----------------
filtered = df[
    (df["Order Date"].dt.date >= date_range[0]) &
    (df["Order Date"].dt.date <= date_range[1]) &
    (df["Status"].isin(status_filter)) &
    (df["Payment Type"].isin(payment_filter))
]

# Apply UTM filters if available
if utm_filter and "Utm Source" in filtered.columns:
    filtered = filtered[filtered["Utm Source"].isin(utm_filter)]

if campaign_filter and "Utm Campaign" in filtered.columns:
    filtered = filtered[filtered["Utm Campaign"].isin(campaign_filter)]

# ---------------- KEY METRICS ----------------
st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

total_orders = filtered["Order Number"].nunique()
total_revenue = filtered["Grand Total"].sum()
avg_order_value = filtered["Grand Total"].mean()
prepaid_orders = filtered[filtered["Payment Type"] == "Prepaid"].shape[0]
cod_orders = filtered[filtered["Payment Type"] == "COD"].shape[0]

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

# ---------------- ROW 1: TRENDS ----------------
st.markdown('<div class="section-header">📊 Revenue & Order Trends</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Daily revenue and orders trend
    daily = filtered.groupby(filtered["Order Date"].dt.date).agg({
        "Grand Total": "sum",
        "Order Number": "count"
    }).reset_index()
    daily.columns = ["Date", "Revenue", "Orders"]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=daily["Date"], 
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
            x=daily["Date"], 
            y=daily["Orders"],
            name="Orders",
            line=dict(color='#f093fb', width=2, dash='dot'),
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title="Daily Revenue & Orders",
        height=350,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0', secondary_y=False)
    fig.update_yaxes(showgrid=False, secondary_y=True)
    
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
        title="Payment Split",
        height=350,
        showlegend=False,
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=14, color='#1a1a1a'),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 2: STATUS & GEOGRAPHY ----------------
st.markdown('<div class="section-header">🗺️ Geographic & Status Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Top states
    if "Billing State" in filtered.columns:
        state_data = filtered.groupby("Billing State").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        state_data.columns = ["State", "Orders", "Revenue"]
        state_data = state_data.sort_values("Orders", ascending=True).tail(10)
        
        fig = go.Figure(go.Bar(
            x=state_data["Orders"],
            y=state_data["State"],
            orientation='h',
            marker=dict(
                color=state_data["Orders"],
                colorscale='Blues',
                showscale=False
            ),
            text=state_data["Orders"],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Top 10 States by Orders",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            yaxis=dict(showgrid=False),
            font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Order status funnel
    status_counts = filtered["Status"].value_counts().reset_index().head(6)
    status_counts.columns = ["Status", "Orders"]
    
    fig = go.Figure(go.Funnel(
        y=status_counts["Status"],
        x=status_counts["Orders"],
        textinfo="value+percent initial",
        marker=dict(color=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b'])
    ))
    
    fig.update_layout(
        title="Order Status Funnel",
        height=350,
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 3: UTM SOURCE & CAMPAIGN ANALYSIS ----------------
st.markdown('<div class="section-header">📱 Marketing Performance Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # UTM Source analysis
    if "Utm Source" in filtered.columns:
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
            title="UTM Source Performance: Orders & AOV",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, title="Source"),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders"),
            yaxis2=dict(showgrid=False, overlaying='y', side='right', title="AOV (₹)"),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=50),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Campaign analysis
    if "Utm Campaign" in filtered.columns:
        campaign_data = filtered.groupby("Utm Campaign").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        campaign_data.columns = ["Campaign", "Orders", "Revenue"]
        campaign_data = campaign_data.sort_values("Revenue", ascending=True).tail(10)
        
        fig = go.Figure(go.Bar(
            x=campaign_data["Revenue"],
            y=campaign_data["Campaign"],
            orientation='h',
            marker=dict(
                color=campaign_data["Revenue"],
                colorscale='Sunset',
                showscale=False
            ),
            text=[f"₹{x:,.0f}" for x in campaign_data["Revenue"]],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Top 10 Campaigns by Revenue",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Revenue (₹)"),
            yaxis=dict(showgrid=False, title=""),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 3.5: UTM PAYMENT TYPE ANALYSIS ----------------
st.markdown('<div class="section-header">💳 UTM Source - Payment Type Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # UTM Source wise COD vs Prepaid
    if "Utm Source" in filtered.columns:
        utm_payment = filtered.groupby(["Utm Source", "Payment Type"]).agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        
        # Get top 10 sources by total orders
        top_sources = filtered.groupby("Utm Source")["Order Number"].count().nlargest(10).index.tolist()
        utm_payment = utm_payment[utm_payment["Utm Source"].isin(top_sources)]
        
        fig = go.Figure()
        
        for payment_type in ["Prepaid", "COD"]:
            data = utm_payment[utm_payment["Payment Type"] == payment_type]
            fig.add_trace(go.Bar(
                name=payment_type,
                x=data["Utm Source"],
                y=data["Order Number"],
                marker=dict(color='#4facfe' if payment_type == "Prepaid" else '#f093fb'),
                text=data["Order Number"],
                textposition='outside'
            ))
        
        fig.update_layout(
            title="UTM Source: COD vs Prepaid Orders (Top 10)",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            barmode='group',
            xaxis=dict(showgrid=False, tickangle=-45, title="UTM Source"),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders"),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=100),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Prepaid % by UTM Source
    if "Utm Source" in filtered.columns:
        utm_prepaid = filtered.groupby(["Utm Source", "Payment Type"]).size().unstack(fill_value=0)
        utm_prepaid["Total"] = utm_prepaid.sum(axis=1)
        utm_prepaid["Prepaid %"] = (utm_prepaid.get("Prepaid", 0) / utm_prepaid["Total"] * 100)
        utm_prepaid = utm_prepaid.sort_values("Total", ascending=False).head(10).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=utm_prepaid["Utm Source"],
            y=utm_prepaid["Prepaid %"],
            marker=dict(
                color=utm_prepaid["Prepaid %"],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Prepaid %"),
                cmin=0,
                cmax=100
            ),
            text=[f"{x:.1f}%" for x in utm_prepaid["Prepaid %"]],
            textposition='outside'
        ))
        
        # Add reference line at 50%
        fig.add_hline(y=50, line_dash="dash", line_color="gray", 
                     annotation_text="50% threshold", annotation_position="right")
        
        fig.update_layout(
            title="Prepaid % by UTM Source (Top 10)",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickangle=-45, title="UTM Source"),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Prepaid %", range=[0, 105]),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=100)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 4: PRODUCTS & PAYMENT MIX ----------------
st.markdown('<div class="section-header">🛍️ Product Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Top products
    if "Product Name" in filtered.columns:
        product_data = filtered.groupby("Product Name").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        product_data.columns = ["Product", "Orders", "Revenue"]
        product_data = product_data.sort_values("Orders", ascending=False).head(10)
        
        fig = go.Figure(data=[
            go.Bar(
                x=product_data["Product"],
                y=product_data["Orders"],
                marker=dict(
                    color=product_data["Revenue"],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Revenue (₹)")
                ),
                text=product_data["Orders"],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="Top 10 Products by Orders",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            font=dict(family="Arial, sans-serif", size=12, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=80)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Product-wise payment split
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
            title="Product-wise Payment Split (Top 8)",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            barmode='stack',
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders"),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=80),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 5: RTO ANALYSIS ----------------
st.markdown('<div class="section-header">⚠️ RTO Risk Analysis</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if "RTO Risk" in filtered.columns:
        rto_risk = filtered["RTO Risk"].value_counts().reset_index()
        rto_risk.columns = ["Risk Level", "Orders"]
        
        fig = go.Figure(data=[
            go.Bar(
                x=rto_risk["Risk Level"],
                y=rto_risk["Orders"],
                marker=dict(
                    color=['#43e97b', '#fee140', '#fa709a', '#f093fb'],
                ),
                text=rto_risk["Orders"],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="RTO Risk Distribution",
            height=280,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if "RTO Score" in filtered.columns:
        fig = go.Figure(data=[go.Histogram(
            x=filtered["RTO Score"],
            nbinsx=30,
            marker=dict(
                color='#fa709a',
                line=dict(color='white', width=1)
            )
        )])
        
        fig.update_layout(
            title="RTO Score Distribution",
            height=280,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="RTO Score",
            yaxis_title="Count",
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col3:
    # RTO metrics
    if "RTO Risk" in filtered.columns:
        high_risk = filtered[filtered["RTO Risk"].str.contains("High", na=False)].shape[0]
        high_risk_pct = (high_risk / len(filtered) * 100) if len(filtered) > 0 else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">High Risk Orders</div>
            <div class="metric-value">{high_risk:,}</div>
            <div style="color: #fa709a; font-size: 16px;">{high_risk_pct:.1f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
        
        avg_rto_score = filtered["RTO Score"].mean() if "RTO Score" in filtered.columns else 0
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 20px;">
            <div class="metric-label">Avg RTO Score</div>
            <div class="metric-value">{avg_rto_score:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- ROW 6: TIME-BASED ANALYSIS ----------------
st.markdown('<div class="section-header">⏰ Time-Based Performance</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    # Day of week analysis
    filtered["Day of Week"] = filtered["Order Date"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    dow_data = filtered.groupby("Day of Week").agg({
        "Order Number": "count",
        "Grand Total": "sum"
    }).reindex(day_order).reset_index()
    dow_data.columns = ["Day", "Orders", "Revenue"]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dow_data["Day"],
        y=dow_data["Orders"],
        marker=dict(
            color=['#667eea', '#764ba2', '#f093fb', '#fa709a', '#fee140', '#30cfd0', '#43e97b']
        ),
        text=dow_data["Orders"],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Orders by Day of Week",
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        font=dict(family="Arial, sans-serif", size=10, color='#1a1a1a'),
        margin=dict(l=40, r=40, t=40, b=80)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Hour of day analysis
    filtered["Hour"] = filtered["Order Date"].dt.hour
    
    hour_data = filtered.groupby("Hour")["Order Number"].count().reset_index()
    hour_data.columns = ["Hour", "Orders"]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hour_data["Hour"],
        y=hour_data["Orders"],
        mode='lines+markers',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#764ba2'),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))
    
    fig.update_layout(
        title="Orders by Hour of Day",
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Hour", dtick=2),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Orders"),
        font=dict(family="Arial, sans-serif", size=10, color='#1a1a1a'),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col3:
    # Weekly trend
    filtered["Week"] = filtered["Order Date"].dt.to_period('W').astype(str)
    
    weekly_data = filtered.groupby("Week").agg({
        "Order Number": "count",
        "Grand Total": "sum"
    }).reset_index()
    weekly_data.columns = ["Week", "Orders", "Revenue"]
    weekly_data["AOV"] = weekly_data["Revenue"] / weekly_data["Orders"]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=weekly_data["Week"],
        y=weekly_data["AOV"],
        mode='lines+markers',
        line=dict(color='#f093fb', width=3),
        marker=dict(size=8, color='#fa709a'),
        fill='tozeroy',
        fillcolor='rgba(240, 147, 251, 0.2)'
    ))
    
    fig.update_layout(
        title="Weekly Average Order Value",
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False, tickangle=-45, title="Week"),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="AOV (₹)"),
        font=dict(family="Arial, sans-serif", size=10, color='#1a1a1a'),
        margin=dict(l=40, r=40, t=40, b=80)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 7: CUSTOMER INSIGHTS & LIFETIME VALUE ----------------
st.markdown('<div class="section-header">👥 Customer Insights & Lifetime Value</div>', unsafe_allow_html=True)

# Calculate Customer Lifetime Value metrics
if "Customer Name" in filtered.columns:
    clv_data = df.groupby("Customer Name").agg({
        "Order Number": "count",
        "Grand Total": "sum",
        "Order Date": ["min", "max"]
    }).reset_index()
    
    clv_data.columns = ["Customer", "Total Orders", "Total Revenue", "First Order", "Last Order"]
    clv_data["Customer Lifetime (Days)"] = (clv_data["Last Order"] - clv_data["First Order"]).dt.days
    clv_data["Avg Order Value"] = clv_data["Total Revenue"] / clv_data["Total Orders"]
    
    # Calculate repeat customer rate
    repeat_customers = clv_data[clv_data["Total Orders"] > 1].shape[0]
    total_customers = clv_data.shape[0]
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    # CLV KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Total Customers", 
            f"{total_customers:,}"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Repeat Customers", 
            f"{repeat_customers:,}",
            f"{repeat_rate:.1f}%"
        ), unsafe_allow_html=True)
    
    with col3:
        avg_clv = clv_data["Total Revenue"].mean()
        st.markdown(create_metric_card(
            "Avg Customer LTV", 
            f"₹{avg_clv:,.0f}"
        ), unsafe_allow_html=True)
    
    with col4:
        avg_orders_per_customer = clv_data["Total Orders"].mean()
        st.markdown(create_metric_card(
            "Avg Orders/Customer", 
            f"{avg_orders_per_customer:.2f}"
        ), unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Top customers by CLV
    if "Customer Name" in filtered.columns:
        top_clv = clv_data.sort_values("Total Revenue", ascending=False).head(15)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=top_clv["Customer"],
            y=top_clv["Total Revenue"],
            name="Total Revenue",
            marker=dict(color='#667eea'),
            text=[f"₹{x:,.0f}" for x in top_clv["Total Revenue"]],
            textposition='outside',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=top_clv["Customer"],
            y=top_clv["Total Orders"],
            name="Orders",
            mode='lines+markers',
            marker=dict(color='#f093fb', size=10),
            line=dict(color='#f093fb', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Top 15 Customers by Lifetime Value",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickangle=-45, title="Customer"),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Total Revenue (₹)"),
            yaxis2=dict(showgrid=False, overlaying='y', side='right', title="Total Orders"),
            font=dict(family="Arial, sans-serif", size=10, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=120),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Customer segmentation by order frequency
    if "Customer Name" in filtered.columns:
        clv_data["Segment"] = pd.cut(
            clv_data["Total Orders"], 
            bins=[0, 1, 3, 5, float('inf')],
            labels=["One-time", "Occasional (2-3)", "Regular (4-5)", "Loyal (6+)"]
        )
        
        segment_data = clv_data.groupby("Segment").agg({
            "Customer": "count",
            "Total Revenue": "sum"
        }).reset_index()
        segment_data.columns = ["Segment", "Customers", "Revenue"]
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "domain"}, {"type": "domain"}]],
            subplot_titles=("By Customer Count", "By Revenue")
        )
        
        fig.add_trace(go.Pie(
            labels=segment_data["Segment"],
            values=segment_data["Customers"],
            hole=0.4,
            marker=dict(colors=['#fa709a', '#fee140', '#30cfd0', '#43e97b']),
            textinfo='label+percent',
            textfont_size=11
        ), 1, 1)
        
        fig.add_trace(go.Pie(
            labels=segment_data["Segment"],
            values=segment_data["Revenue"],
            hole=0.4,
            marker=dict(colors=['#fa709a', '#fee140', '#30cfd0', '#43e97b']),
            textinfo='label+percent',
            textfont_size=11
        ), 1, 2)
        
        fig.update_layout(
            title_text="Customer Segmentation",
            height=350,
            showlegend=False,
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Cohort analysis
col1, col2 = st.columns(2)

with col1:
    # Order frequency distribution
    if "Customer Name" in filtered.columns:
        order_freq = clv_data["Total Orders"].value_counts().sort_index().reset_index()
        order_freq.columns = ["Orders", "Customers"]
        order_freq = order_freq[order_freq["Orders"] <= 10]  # Limit to 10 orders for clarity
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=order_freq["Orders"],
            y=order_freq["Customers"],
            marker=dict(
                color=order_freq["Customers"],
                colorscale='Viridis',
                showscale=False
            ),
            text=order_freq["Customers"],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Customer Distribution by Order Count",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, title="Number of Orders", dtick=1),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Number of Customers"),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Customer lifetime duration vs revenue
    if "Customer Name" in filtered.columns:
        active_clv = clv_data[clv_data["Customer Lifetime (Days)"] > 0]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=active_clv["Customer Lifetime (Days)"],
            y=active_clv["Total Revenue"],
            mode='markers',
            marker=dict(
                size=active_clv["Total Orders"] * 3,
                color=active_clv["Total Orders"],
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title="Orders"),
                line=dict(color='white', width=0.5)
            ),
            text=active_clv["Customer"],
            hovertemplate='<b>%{text}</b><br>Lifetime: %{x} days<br>Revenue: ₹%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Customer Lifetime vs Revenue (bubble = order count)",
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Customer Lifetime (Days)"),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Total Revenue (₹)"),
            font=dict(family="Arial, sans-serif", size=11, color='#1a1a1a'),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- DATA TABLE ----------------
st.markdown('<div class="section-header">📋 Detailed Order Data</div>', unsafe_allow_html=True)

display_cols = [
    "Order Number", "Order Date", "Status", "Payment Method", 
    "Grand Total", "Customer Name", "Billing State", "Product Name"
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
