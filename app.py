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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
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

    # Data cleaning
    df["Order Date"] = pd.to_datetime(df["Created At"], format="%d-%m-%Y %H:%M", errors="coerce")
    
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
    # Don't stop here, continue to show dashboard

# ---------------- LOAD DATA ----------------
if not uploaded_file:
    df = load_data()
    if df is None:
        st.info("👆 Please upload a file to view the dashboard")
        st.stop()
else:
    # Use the df we just processed
    pass

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
        height=400,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
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
        marker=dict(colors=['#667eea', '#f093fb']),
        textinfo='label+percent',
        textfont_size=14
    )])
    
    fig.update_layout(
        title="Payment Split",
        height=400,
        showlegend=True,
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
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
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            yaxis=dict(showgrid=False),
            font=dict(family="Arial, sans-serif")
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
        height=400,
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 3: PRODUCTS & UTM ----------------
st.markdown('<div class="section-header">🛍️ Product & Marketing Analysis</div>', unsafe_allow_html=True)

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
                    colorbar=dict(title="Revenue")
                ),
                text=product_data["Orders"],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="Top 10 Products by Orders",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            font=dict(family="Arial, sans-serif")
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # UTM source analysis
    if "Utm Source" in filtered.columns:
        utm_data = filtered.groupby("Utm Source").agg({
            "Order Number": "count",
            "Grand Total": "sum"
        }).reset_index()
        utm_data.columns = ["Source", "Orders", "Revenue"]
        utm_data = utm_data.sort_values("Orders", ascending=False).head(8)
        
        fig = go.Figure(data=[
            go.Bar(
                x=utm_data["Source"],
                y=utm_data["Orders"],
                marker=dict(
                    color=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140'],
                ),
                text=utm_data["Orders"],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="Traffic Source Performance",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            font=dict(family="Arial, sans-serif")
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- ROW 4: RTO ANALYSIS ----------------
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
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif")
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
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="RTO Score",
            yaxis_title="Count",
            font=dict(family="Arial, sans-serif")
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
