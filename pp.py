
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(layout="wide", page_title="Process Improvement Analytics - Demo")

# Custom CSS for presentation mode
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        padding: 2rem 0;
    }
    .slide-title {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .kpi-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .kpi-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .insight-box {
        background-color: #e8f4f8;
        border-left: 5px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .recommendation-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        padding: 0.75rem;
        font-size: 1.1rem;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for slide navigation
if 'slide' not in st.session_state:
    st.session_state.slide = 0

# Generate sample data
@st.cache_data
def generate_sample_retail_data():
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    cities = ['Toronto', 'Montreal', 'Vancouver', 'Calgary', 'Ottawa']
    provinces = {'Toronto': 'ON', 'Montreal': 'QC', 'Vancouver': 'BC', 'Calgary': 'AB', 'Ottawa': 'ON'}
    categories = ['Electronics', 'Apparel', 'Home & Garden', 'Sports & Outdoors']

    data = []
    for i, date in enumerate(dates):
        for _ in range(np.random.randint(30, 50)):
            city = np.random.choice(cities)
            data.append({
                'order_id': f'ORD{i}{_:03d}',
                'sales_date': date,
                'city': city,
                'province': provinces[city],
                'product_category': np.random.choice(categories),
                'unit_price': np.random.uniform(20, 500),
                'quantity': np.random.randint(1, 5),
                'discount': np.random.uniform(0, 0.3),
                'return_flag': np.random.choice([True, False], p=[0.07, 0.93])
            })

    df = pd.DataFrame(data)
    df['total_revenue'] = df['unit_price'] * df['quantity']
    df['discount_amount'] = df['total_revenue'] * df['discount']
    df['net_revenue'] = df['total_revenue'] - df['discount_amount']
    return df

@st.cache_data
def generate_sample_supply_chain_data():
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    carriers = ['UPS', 'FedEx', 'USPS', 'DHL']
    states = ['NY', 'CA', 'TX', 'IL', 'WA']
    product_types = ['Electronics', 'Apparel', 'Furniture', 'Books']

    data = []
    for i, date in enumerate(dates):
        for _ in range(np.random.randint(50, 80)):
            carrier = np.random.choice(carriers)
            delivery_days_base = {'UPS': 3.8, 'FedEx': 4.2, 'USPS': 5.8, 'DHL': 6.3}
            issue_rate = {'UPS': 0.05, 'FedEx': 0.07, 'USPS': 0.12, 'DHL': 0.16}

            data.append({
                'shipment_id': f'S{i}{_:03d}',
                'shipment_date': date,
                'delivery_date': date + timedelta(days=int(np.random.normal(delivery_days_base[carrier], 1.5))),
                'origin_state': np.random.choice(states),
                'destination_state': np.random.choice(states),
                'product_type': np.random.choice(product_types),
                'carrier': carrier,
                'issues_flag': np.random.choice([True, False], p=[issue_rate[carrier], 1-issue_rate[carrier]]),
                'weight_kg': np.random.uniform(1, 50)
            })

    df = pd.DataFrame(data)
    df['delivery_days'] = (df['delivery_date'] - df['shipment_date']).dt.days
    df['delivery_days'] = df['delivery_days'].clip(lower=1)
    return df

@st.cache_data
def generate_sample_support_data():
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='H')
    teams = ['Frontline', 'Technical', 'Escalation']
    categories = ['Login Issue', 'Bug Report', 'Feature Request', 'Payment Issue', 'Account Setup']
    priorities = ['High', 'Medium', 'Low']

    data = []
    for i, date in enumerate(dates[:10000]):
        team = np.random.choice(teams, p=[0.6, 0.3, 0.1])
        category = np.random.choice(categories)

        res_time_base = {
            'Frontline': 3.2, 'Technical': 9.8, 'Escalation': 18.5
        }
        cat_multiplier = {
            'Login Issue': 0.5, 'Bug Report': 3.5, 'Feature Request': 2.5,
            'Payment Issue': 4.5, 'Account Setup': 0.7
        }

        resolution_hours = np.random.normal(
            res_time_base[team] * cat_multiplier[category], 
            res_time_base[team] * 0.5
        )
        resolution_hours = max(0.1, resolution_hours)

        data.append({
            'ticket_id': f'T{i:05d}',
            'opened_at': date,
            'closed_at': date + timedelta(hours=resolution_hours),
            'agent_team': team,
            'category': category,
            'priority': np.random.choice(priorities),
            'resolution_hours': resolution_hours,
            'csat_score': np.random.uniform(3.5, 5.0)
        })

    return pd.DataFrame(data)

# Load sample data
retail_df = generate_sample_retail_data()
supply_chain_df = generate_sample_supply_chain_data()
support_df = generate_sample_support_data()

# Slide definitions
def slide_1_overview():
    st.markdown('<div class="main-title">📊 Process Improvement Data Analytics Platform</div>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 🛒 Retail Sales Optimization
        **Market:** Canada

        ✅ Sales trend analysis  
        ✅ Regional performance  
        ✅ Category insights  
        ✅ Revenue optimization
        """)

    with col2:
        st.markdown("""
        ### 🚚 Supply Chain Efficiency
        **Market:** North America

        ✅ Delivery time tracking  
        ✅ Carrier performance  
        ✅ Issue rate analysis  
        ✅ Route optimization
        """)

    with col3:
        st.markdown("""
        ### 🎧 Customer Support
        **Market:** North America

        ✅ Resolution time tracking  
        ✅ Team performance  
        ✅ CSAT analysis  
        ✅ Category insights
        """)

    st.markdown("---")
    st.markdown("""
    ### 🛠️ Technology Stack
    **Backend:** Python, Pandas, NumPy | **Frontend:** Streamlit, Plotly | **Database:** SQL (PostgreSQL/MySQL)
    """)

def slide_2_retail_dashboard():
    st.markdown('<div class="slide-title">🛒 Retail Sales Optimization Dashboard</div>', unsafe_allow_html=True)

    # Filters in sidebar
    with st.sidebar:
        st.header("📋 Filters")
        selected_provinces = st.multiselect("Province", retail_df['province'].unique(), default=retail_df['province'].unique())
        selected_categories = st.multiselect("Category", retail_df['product_category'].unique(), default=retail_df['product_category'].unique())

    filtered_df = retail_df[
        (retail_df['province'].isin(selected_provinces)) &
        (retail_df['product_category'].isin(selected_categories))
    ]

    # KPIs
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    total_revenue = filtered_df['net_revenue'].sum()
    avg_revenue = filtered_df['net_revenue'].mean()
    total_transactions = len(filtered_df)
    avg_discount = filtered_df['discount'].mean() * 100

    with col1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Total Revenue (CAD)</div>
            <div class="kpi-value">${total_revenue:,.0f}</div>
            <div style="color: #90EE90;">↑ 12.3%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Avg Revenue/Transaction</div>
            <div class="kpi-value">${avg_revenue:,.2f}</div>
            <div style="color: #90EE90;">↑ 3.5%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Total Transactions</div>
            <div class="kpi-value">{total_transactions:,}</div>
            <div style="color: #90EE90;">↑ 8.6%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Avg Discount (%)</div>
            <div class="kpi-value">{avg_discount:.1f}%</div>
            <div style="color: #FFB6C1;">↓ 2.1%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Sales trend
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Daily Revenue Trend")
        daily_sales = filtered_df.groupby('sales_date')['net_revenue'].sum().reset_index()
        fig1 = px.line(daily_sales, x='sales_date', y='net_revenue',
                      labels={'net_revenue': 'Net Revenue (CAD)', 'sales_date': 'Date'})
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("🥇 Top Categories")
        category_revenue = filtered_df.groupby('product_category')['net_revenue'].sum().sort_values(ascending=True)
        fig2 = px.bar(category_revenue, orientation='h',
                     labels={'value': 'Revenue (CAD)', 'product_category': 'Category'})
        fig2.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <strong>💡 Key Insight:</strong> Electronics category generates 43% of total revenue. Peak sales occur during June-July (summer season).
    </div>
    """, unsafe_allow_html=True)

def slide_3_retail_province():
    st.markdown('<div class="slide-title">🗺️ Provincial Performance Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Revenue Distribution by Province")
        province_revenue = retail_df.groupby('province')['net_revenue'].sum().reset_index()
        fig = px.pie(province_revenue, values='net_revenue', names='province',
                    title='Revenue Share by Province')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Provincial Breakdown")
        province_stats = retail_df.groupby('province').agg({
            'net_revenue': 'sum',
            'order_id': 'count'
        }).round(2)
        province_stats.columns = ['Total Revenue', 'Transactions']
        province_stats['% of Total'] = (province_stats['Total Revenue'] / province_stats['Total Revenue'].sum() * 100).round(1)
        province_stats = province_stats.sort_values('Total Revenue', ascending=False)

        st.dataframe(province_stats.style.format({
            'Total Revenue': '${:,.0f}',
            'Transactions': '{:,}',
            '% of Total': '{:.1f}%'
        }), use_container_width=True)

        st.markdown("""
        <div class="recommendation-box">
            <strong>💡 Recommendations:</strong><br>
            • Ontario (ON) generates 42% of revenue - maintain strong presence<br>
            • Consider expanding operations in BC and AB (growth opportunity)<br>
            • Focus marketing efforts on high-performing provinces
        </div>
        """, unsafe_allow_html=True)

def slide_4_supply_chain_dashboard():
    st.markdown('<div class="slide-title">🚚 Supply Chain Efficiency Dashboard</div>', unsafe_allow_html=True)

    # KPIs
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    avg_delivery = supply_chain_df['delivery_days'].mean()
    median_delivery = supply_chain_df['delivery_days'].median()
    issue_rate = supply_chain_df['issues_flag'].mean() * 100
    total_shipments = len(supply_chain_df)

    with col1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Avg Delivery Days</div>
            <div class="kpi-value">{avg_delivery:.1f}</div>
            <div style="color: #90EE90;">↓ 0.5 days</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Median Delivery Days</div>
            <div class="kpi-value">{median_delivery:.1f}</div>
            <div style="color: #90EE90;">↓ 0.3 days</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Issue Rate</div>
            <div class="kpi-value">{issue_rate:.1f}%</div>
            <div style="color: #90EE90;">↓ 1.2%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Total Shipments</div>
            <div class="kpi-value">{total_shipments:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Carrier performance
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Delivery Days by Carrier")
        carrier_perf = supply_chain_df.groupby('carrier')['delivery_days'].agg(['mean', 'std', 'count']).round(2)
        carrier_perf = carrier_perf.sort_values('mean')

        fig = px.bar(carrier_perf.reset_index(), x='carrier', y='mean', error_y='std',
                    labels={'mean': 'Avg Delivery Days', 'carrier': 'Carrier'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("⚠️ Issue Rate by Carrier")
        carrier_issues = supply_chain_df.groupby('carrier')['issues_flag'].agg(['sum', 'count'])
        carrier_issues['rate'] = (carrier_issues['sum'] / carrier_issues['count'] * 100).round(1)
        carrier_issues = carrier_issues.sort_values('rate')

        fig = px.bar(carrier_issues.reset_index(), x='carrier', y='rate',
                    labels={'rate': 'Issue Rate (%)', 'carrier': 'Carrier'},
                    color='rate', color_continuous_scale='Reds')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="recommendation-box">
        <strong>🚨 Critical Action Required:</strong><br>
        • DHL has 16% issue rate vs UPS 5% - reduce DHL volume by 50%<br>
        • UPS shows best performance - consider increasing volume<br>
        • Optimize routes for high-delay carriers
    </div>
    """, unsafe_allow_html=True)

def slide_5_support_dashboard():
    st.markdown('<div class="slide-title">🎧 Customer Support Dashboard</div>', unsafe_allow_html=True)

    # KPIs
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    avg_resolution = support_df['resolution_hours'].mean()
    median_resolution = support_df['resolution_hours'].median()
    avg_csat = support_df['csat_score'].mean()
    total_tickets = len(support_df)

    with col1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Avg Resolution (hrs)</div>
            <div class="kpi-value">{avg_resolution:.1f}</div>
            <div style="color: #90EE90;">↓ 1.5 hrs</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Median Resolution (hrs)</div>
            <div class="kpi-value">{median_resolution:.1f}</div>
            <div style="color: #90EE90;">↓ 0.8 hrs</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Avg CSAT Score</div>
            <div class="kpi-value">{avg_csat:.2f}/5.0</div>
            <div style="color: #90EE90;">↑ 0.3</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Resolved Tickets</div>
            <div class="kpi-value">{total_tickets:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👥 Resolution Time by Team")
        team_perf = support_df.groupby('agent_team')['resolution_hours'].agg(['mean', 'count']).round(2)
        team_perf = team_perf.sort_values('mean')

        fig = px.bar(team_perf.reset_index(), x='agent_team', y='mean',
                    labels={'mean': 'Avg Resolution Hours', 'agent_team': 'Team'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📋 Resolution Time by Category")
        category_perf = support_df.groupby('category')['resolution_hours'].agg(['mean', 'count']).round(2)
        category_perf = category_perf.sort_values('mean', ascending=False)

        fig = px.bar(category_perf.reset_index(), x='mean', y='category', orientation='h',
                    labels={'mean': 'Avg Resolution Hours', 'category': 'Category'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="recommendation-box">
        <strong>💡 Recommendations:</strong><br>
        • Implement chatbot for Login Issues (1.8h avg - easily automated)<br>
        • Train 3 agents on Payment Issues (15.7h avg - longest resolution)<br>
        • Review Escalation team processes (5.8x slower than Frontline)
    </div>
    """, unsafe_allow_html=True)

def slide_6_summary():
    st.markdown('<div class="slide-title">🎯 Process Improvement Summary</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 🛒 Retail Optimization

        **Key Findings:**
        - 📈 Revenue up 12.3%
        - 🏆 Electronics: 43% of revenue
        - 🗺️ Ontario: 42% market share

        **Actions:**
        ✅ Increase Electronics marketing  
        ✅ Expand BC/AB operations  
        ✅ Optimize seasonal inventory
        """)

    with col2:
        st.markdown("""
        ### 🚚 Supply Chain

        **Key Findings:**
        - ⏱️ Avg delivery: 4.8 days (↓0.5)
        - 🚨 DHL: 16% issue rate
        - ⭐ UPS: Best performer (5%)

        **Actions:**
        ✅ Reduce DHL volume 50%  
        ✅ Increase UPS contracts  
        ✅ Route optimization
        """)

    with col3:
        st.markdown("""
        ### 🎧 Customer Support

        **Key Findings:**
        - ⏱️ Avg resolution: 8.3h (↓1.5)
        - 💳 Payment issues: 15.7h
        - 🤖 Login issues: 1.8h

        **Actions:**
        ✅ Automate login resets  
        ✅ Train payment specialists  
        ✅ Escalation process review
        """)

    st.markdown("---")

    st.markdown("""
    <div class="insight-box">
        <h3>🚀 Overall Impact</h3>
        <strong>Estimated Annual Savings:</strong><br>
        • Retail optimization: $425K in reduced waste<br>
        • Supply chain efficiency: $280K in faster deliveries<br>
        • Support automation: $190K in labor costs<br>
        <br>
        <strong>Total Projected Savings: $895,000/year</strong>
    </div>
    """, unsafe_allow_html=True)

# Slide navigation
slides = [
    ("Overview", slide_1_overview),
    ("Retail Dashboard", slide_2_retail_dashboard),
    ("Provincial Analysis", slide_3_retail_province),
    ("Supply Chain Dashboard", slide_4_supply_chain_dashboard),
    ("Customer Support", slide_5_support_dashboard),
    ("Summary & ROI", slide_6_summary)
]

# Sidebar navigation
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎬 Presentation Navigation")
st.sidebar.markdown(f"**Slide {st.session_state.slide + 1} of {len(slides)}**")

for i, (title, _) in enumerate(slides):
    if st.sidebar.button(f"{i+1}. {title}", key=f"nav_{i}"):
        st.session_state.slide = i

st.sidebar.markdown("---")

# Navigation buttons
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅️ Previous", disabled=(st.session_state.slide == 0)):
        st.session_state.slide = max(0, st.session_state.slide - 1)
        st.rerun()

with col2:
    st.markdown(f"<h3 style='text-align: center;'>Slide {st.session_state.slide + 1}/{len(slides)}</h3>", unsafe_allow_html=True)

with col3:
    if st.button("Next ➡️", disabled=(st.session_state.slide == len(slides) - 1)):
        st.session_state.slide = min(len(slides) - 1, st.session_state.slide + 1)
        st.rerun()

st.markdown("---")

# Display current slide
current_slide_func = slides[st.session_state.slide][1]
current_slide_func()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>📊 Process Improvement Data Analytics Platform | Built with Python & Streamlit</p>
    <p>💼 Ready for Canadian & North American Markets | 🚀 Production-Ready Code</p>
</div>
""", unsafe_allow_html=True)
