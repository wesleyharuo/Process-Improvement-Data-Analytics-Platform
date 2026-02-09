import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------

@st.cache_data
def load_data_from_csv(uploaded_file):
    """
    Reads and returns a DataFrame from an uploaded CSV.
    Caching ensures the file is read only once per upload.
    """
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df
    return None

# ------------------------------------------------------------

uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv", key="file_uploader")

df = load_data_from_csv(uploaded_file)

if df is None:
    st.warning("No data loaded. Please upload a CSV file or ensure built‑in data files are in the correct location.")
    st.stop()
O que acontece aqui:
load_data_from_csv(uploaded_file) é cacheado: o Streamlit guarda o retorno (DataFrame) para o mesmo arquivo até você trocar o upload.

Você não chama pd.read_csv diretamente no st.file_uploader, só dentro da função decorada com st.cache_data.

Assim, se você mover filtros ou sliders, o Streamlit não relê o CSV, só usa o DataFrame já carregado.

✅ 2. Integrando com o menu de projetos
Você já tem o project = st.selectbox(...), então basta usar o mesmo df carregado e aplicar a lógica do template de cada projeto.

Exemplo mínimo adaptado:

python
@st.cache_data
def load_data_from_csv(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df
    return None

uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv", key="file_uploader")
df = load_data_from_csv(uploaded_file)

if df is None:
    st.warning("No data loaded. Please upload a CSV file.")
    st.stop()

# --- 1. Retail Sales Optimization
if project == "Retail Sales Optimization (Canada)":
    st.markdown("## Retail Sales Optimization Dashboard")

    # Auto‑detect columns
    date_col = None
    for c in df.columns:
        if "date" in c.lower() or "order" in c.lower():
            date_col = c
            break
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["month_year"] = df[date_col].dt.to_period("M").astype(str)

    # Auto‑detect revenue column
    revenue_cols = [c for c in df.columns if "revenue" in c.lower() or "sales" in c.lower()]
    revenue_col = revenue_cols[0] if revenue_cols else df.select_dtypes(include="number").columns[0]

    # Auto‑filters
    cat_cols = [c for c in df.columns if "category" in c.lower()]
    cat_col = cat_cols[0] if cat_cols else None

    if cat_col:
        categories = st.sidebar.multiselect("Category", df[cat_col].unique(), default=df[cat_col].unique())
        df = df[df[cat_col].isin(categories)]

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue (CAD)", f"${df[revenue_col].sum():,.0f}")
    col2.metric("Avg Revenue per Transaction", f"${df[revenue_col].mean():,.2f}")
    col3.metric("Total Transactions", len(df))

    # Sales over time
    if date_col:
        time_trend = df.groupby(date_col)[revenue_col].sum().reset_index()
        fig1 = px.line(time_trend, x=date_col, y=revenue_col, title="Daily Revenue")
        st.plotly_chart(fig1, use_container_width=True)
(Repete o padrão para Supply Chain e Customer Support, usando df já carregado pelo st.cache_data.)

✅ 3. Bônus: cache separado para cada projeto
Se você quiser que o app carregue o arquivo de cada projeto diferente (por exemplo, 3 widgets de upload), você pode fazer:

python
@st.cache_data
def load_retail_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return pd.read_csv("data/retail_sales_canada_cleaned.csv")

@st.cache_data
def load_supply_chain_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return pd.read_csv("data/supply_chain_usa_cleaned.csv")

@st.cache_data
def load_support_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return pd.read_csv("data/customer_support_tickets_cleaned.csv")

st.set_page_config(layout="wide", page_title="Process Improvement Dashboards")

st.title("📊 Process Improvement Data Analytics Dashboards")
st.markdown(
    """
    Select a project and optionally upload a **CSV file** to analyze your own data.
    """
)

# =================================================
# Project selector
# =================================================
project = st.selectbox(
    "Select dashboard template",
    options=[
        "Retail Sales Optimization (Canada)",
        "Supply Chain Efficiency (North America)",
        "Customer Support Time Reduction (North America)",
    ],
    key="project_selector",
)

# =================================================
# File uploader (CSV)
# =================================================
st.sidebar.header("Upload your data")
uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV file (or use built‑in sample data)",
    type="csv",
    key="file_uploader",
)

# =================================================
# Cache data loading (works with uploaded files)
# =================================================
@st.cache_data
def load_data_from_upload(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df, "uploaded"
    return None, "uploaded"

@st.cache_data
def load_builtin_retail():
    df = pd.read_csv("data/retail_sales_canada_cleaned.csv")
    df["sales_date"] = pd.to_datetime(df["sales_date"], errors="coerce")
    df["month_year"] = df["sales_date"].dt.to_period("M").astype(str)
    return df

@st.cache_data
def load_builtin_supply_chain():
    df = pd.read_csv("data/supply_chain_usa_cleaned.csv")
    df["shipment_date"] = pd.to_datetime(df["shipment_date"], errors="coerce")
    df["delivery_date"] = pd.to_datetime(df["delivery_date"], errors="coerce")
    df["month_year"] = df["shipment_date"].dt.to_period("M").astype(str)
    return df

@st.cache_data
def load_builtin_support():
    df = pd.read_csv("data/customer_support_tickets_cleaned.csv")
    df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")
    df["closed_at"] = pd.to_datetime(df["closed_at"], errors="coerce")
    df["month_year"] = df["opened_at"].dt.to_period("M").astype(str)
    return df


# =================================================
# Load data based on project + uploaded file
# =================================================
df = None
data_source = None

if uploaded_file is not None:
    df, data_source = load_data_from_upload(uploaded_file)
    if df is not None:
        st.sidebar.success("File loaded successfully.")
elif project == "Retail Sales Optimization (Canada)":
    try:
        df = load_builtin_retail()
        data_source = "builtin_retail"
    except Exception as e:
        st.error("Error loading built‑in retail data. Check that `data/retail_sales_canada_cleaned.csv` exists.")
        st.code(str(e))
        st.stop()
elif project == "Supply Chain Efficiency (North America)":
    try:
        df = load_builtin_supply_chain()
        data_source = "builtin_supply_chain"
    except Exception as e:
        st.error("Error loading built‑in supply chain data. Check that `data/supply_chain_usa_cleaned.csv` exists.")
        st.code(str(e))
        st.stop()
elif project == "Customer Support Time Reduction (North America)":
    try:
        df = load_builtin_support()
        data_source = "builtin_support"
    except Exception as e:
        st.error("Error loading built‑in support data. Check that `data/customer_support_tickets_cleaned.csv` exists.")
        st.code(str(e))
        st.stop()


# If no data is loaded at all
if df is None:
    st.warning("No data loaded. Please upload a CSV file or ensure the built‑in data files are in the correct location.")
    st.image("https://docs.streamlit.io/assets/images/undraw_uploading_re_m6qf.svg", width=300)
    st.stop()


# =================================================
# 1. Retail Sales Optimization (Canada)
# =================================================
if project == "Retail Sales Optimization (Canada)":
    st.markdown("## Retail Sales Optimization Dashboard")
    st.markdown(
        "Analyzing sales performance for a **Canadian retail chain** to improve revenue and reduce waste."
    )

    # Auto‑detect columns (if uploaded) or use hardcoded ones
    date_col = "sales_date" if "sales_date" in df.columns else df.select_dtypes(include="datetime").columns[0] if not df.select_dtypes(include="datetime").empty else None
    if date_col is None:
        st.error("No datetime column found for sales date.")
        st.stop()

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["month_year"] = df[date_col].dt.to_period("M").astype(str)

    cat_col = "product_category" if "product_category" in df.columns else st.selectbox("Select product category column", df.select_dtypes(include="object").columns)
    revenue_cols = [c for c in df.columns if "revenue" in c.lower() or "sales" in c.lower()]
    revenue_col = revenue_cols[0] if revenue_cols else st.selectbox("Select revenue column", df.select_dtypes(include="number").columns)

    # Filters
    st.sidebar.header("Retail Filters")
    cat_options = df[cat_col].unique()
    categories = st.sidebar.multiselect("Product Category", cat_options, default=cat_options)

    city_cols = [c for c in df.columns if "city" in c.lower()]
    city_col = city_cols[0] if city_cols else None
    if city_col:
        cities = st.sidebar.multiselect("City", df[city_col].unique(), default=df[city_col].unique())
    else:
        cities = None

    province_cols = [c for c in df.columns if "province" in c.lower() or "state" in c.lower()]
    province_col = province_cols[0] if province_cols else None
    if province_col:
        provinces = st.sidebar.multiselect("Province", df[province_col].unique(), default=df[province_col].unique())
    else:
        provinces = None

    start_date = st.sidebar.date_input("Start Date", value=df[date_col].min())
    end_date = st.sidebar.date_input("End Date", value=df[date_col].max())

    # Apply filters
    mask = (
        (df[cat_col].isin(categories)) &
        (df[date_col] >= pd.to_datetime(start_date)) &
        (df[date_col] <= pd.to_datetime(end_date))
    )
    if city_col: mask &= df[city_col].isin(cities)
    if province_col: mask &= df[province_col].isin(provinces)

    filtered = df[mask]

    # KPIs
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue (CAD)", f"${filtered[revenue_col].sum():,.0f}")
    col2.metric("Avg Revenue per Transaction", f"${filtered[revenue_col].mean():,.2f}")
    col3.metric("Total Transactions", len(filtered))

    # Sales over time
    st.subheader("Sales Trend")
    sales_by_date = filtered.groupby(date_col)[revenue_col].sum().reset_index()
    fig1 = px.line(
        sales_by_date,
        x=date_col,
        y=revenue_col,
        title="Daily Net Revenue",
        labels={revenue_col: "Net Revenue (CAD)"},
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Top categories
    st.subheader("Top Categories by Revenue")
    top_cats = (
        filtered.groupby(cat_col)[revenue_col]
        .agg(["sum", "count"])
        .sort_values("sum", ascending=False)
    )
    st.dataframe(top_cats)

    fig2 = px.bar(
        top_cats.reset_index(),
        x=cat_col,
        y="sum",
        title="Revenue by Product Category",
        labels={"sum": "Net Revenue (CAD)"},
    )
    st.plotly_chart(fig2, use_container_width=True)


# =================================================
# 2. Supply Chain Efficiency (North America)
# =================================================
elif project == "Supply Chain Efficiency (North America)":
    st.markdown("## Supply Chain Efficiency Dashboard")
    st.markdown(
        "Analyzing delivery performance for a **North American logistics network** to reduce delays and costs."
    )

    date_col = "shipment_date" if "shipment_date" in df.columns else df.select_dtypes(include="datetime").columns[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    delivery_day_cols = [c for c in df.columns if "days" in c.lower() or "delivery" in c.lower()]
    delivery_days_col = delivery_day_cols[0] if delivery_day_cols else st.selectbox("Select delivery days column", df.select_dtypes(include="number").columns)
    issue_cols = [c for c in df.columns if "issue" in c.lower() or "flag" in c.lower()]
    issue_col = issue_cols[0] if issue_cols else None

    df["month_year"] = df[date_col].dt.to_period("M").astype(str)

    # Filters
    st.sidebar.header("Supply Chain Filters")
    origin_cols = [c for c in df.columns if "origin" in c.lower()]
    origin_col = origin_cols[0] if origin_cols else None
    if origin_col:
        origins = st.sidebar.multiselect("Origin", df[origin_col].unique())

    dest_cols = [c for c in df.columns if "destin" in c.lower() or "to" in c.lower()]
    dest_col = dest_cols[0] if dest_cols else None
    if dest_col:
        destinations = st.sidebar.multiselect("Destination", df[dest_col].unique())

    product_type_cols = [c for c in df.columns if "product" in c.lower() or "type" in c.lower()]
    product_type_col = product_type_cols[0] if product_type_cols else None
    product_types = st.sidebar.multiselect(
        "Product Type",
        df[product_type_col].unique() if product_type_col else df.select_dtypes(include="object").columns[0],
        default=df[product_type_col].unique() if product_type_col else df.select_dtypes(include="object").columns[0],
    ) if product_type_col else None

    carrier_cols = [c for c in df.columns if "carrier" in c.lower()]
    carrier_col = carrier_cols[0] if carrier_cols else None
    carriers = st.sidebar.multiselect(
        "Carrier",
        df[carrier_col].unique() if carrier_col else df.select_dtypes(include="object").columns[0],
        default=df[carrier_col].unique() if carrier_col else df.select_dtypes(include="object").columns[0],
    ) if carrier_col else None

    # Apply filters
    filtered = df.copy()
    if origin_col and origin_cols: filtered = filtered[filtered[origin_col].isin(origins)]
    if dest_col and dest_cols: filtered = filtered[filtered[dest_col].isin(destinations)]
    if product_type_col and product_types: filtered = filtered[filtered[product_type_col].isin(product_types)]

    # KPIs
    avg_days = filtered[delivery_days_col].mean()
    med_days = filtered[delivery_days_col].median()
    issues_rate = filtered[issue_col].mean() * 100 if issue_col else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Delivery Days", f"{avg_days:.1f}")
    col2.metric("Median Delivery Days", f"{med_days:.1f}")
    col3.metric("Issue Rate (%)", f"{issues_rate:.1f}%")
    col4.metric("Total Shipments", len(filtered))

    # Time trend
    st.subheader("Delivery Days Over Time")
    time_trend = filtered.groupby("month_year")[delivery_days_col].mean().reset_index()
    fig1 = px.line(
        time_trend,
        x="month_year",
        y=delivery_days_col,
        title="Average Delivery Time by Month",
        labels={delivery_days_col: "Avg Delivery Days"},
    )
    st.plotly_chart(fig1, use_container_width=True)


# =================================================
# 3. Customer Support Time Reduction (North America)
# =================================================
elif project == "Customer Support Time Reduction (North America)":
    st.markdown("## Customer Support Time Reduction Dashboard")
    st.markdown(
        "Analyzing ticket resolution for a **North American tech support team** to reduce resolution time and improve CSAT."
    )

    date_col = "opened_at" if "opened_at" in df.columns else df.select_dtypes(include="datetime").columns[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    closed_cols = [c for c in df.columns if "closed" in c.lower()]
    closed_col = closed_cols[0] if closed_cols else None

    res_col = "resolution_hours" if "resolution_hours" in df.columns else st.selectbox("Select resolution time column (hours)", df.select_dtypes(include="number").columns)

    df["month_year"] = df[date_col].dt.to_period("M").astype(str)

    # Filters
    st.sidebar.header("Support Filters")
    team_cols = [c for c in df.columns if "team" in c.lower()]
    team_col = team_cols[0] if team_cols else None
    if team_col:
        teams = st.sidebar.multiselect("Agent Team", df[team_col].unique())

    cat_cols = [c for c in df.columns if "category" in c.lower() or "type" in c.lower()]
    cat_col = cat_cols[0] if cat_cols else None
    categories = st.sidebar.multiselect(
        "Ticket Category",
        df[cat_col].unique() if cat_col else df.select_dtypes(include="object").columns[0],
        default=df[cat_col].unique() if cat_col else df.select_dtypes(include="object").columns[0],
    ) if cat_col else None

    # Apply filters
    filtered = df.copy()
    if team_col and team_cols: filtered = filtered[filtered[team_col].isin(teams)]
    if cat_col and cat_cols: filtered = filtered[filtered[cat_col].isin(categories)]

    # KPIs
    avg_hours = filtered[res_col].mean()
    med_hours = filtered[res_col].median()
    csat_cols = [c for c in df.columns if "csat" in c.lower()]
    csat_col = csat_cols[0] if csat_cols else None
    csat = filtered[csat_col].mean() if csat_col else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Resolution Time (hrs)", f"{avg_hours:.1f}")
    col2.metric("Median Resolution Time (hrs)", f"{med_hours:.1f}")
    col3.metric("Resolved Tickets", len(filtered))

    # Time trend
    st.subheader("Resolution Time Over Time")
    time_trend = filtered.groupby("month_year")[res_col].mean().reset_index()
    fig1 = px.line(
        time_trend,
        x="month_year",
        y=res_col,
        title="Avg Resolution Time by Month",
        labels={res_col: "Avg Resolution Time (hours)"},
    )
    st.plotly_chart(fig1, use_container_width=True)

if project == "Retail Sales Optimization (Canada)":
    uploaded_file = st.sidebar.file_uploader("Upload retail CSV", type="csv")
    df = load_retail_data(uploaded_file)
