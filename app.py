from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# ⚙️ 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sales Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 📂 2. DATA FILE PATH
# ============================================================

DATA_FILE = Path(__file__).resolve().parent / "project Data new.xlsx"


# ============================================================
# 🧹 3. DATA LOADING & CLEANING
# ============================================================

@st.cache_data
def load_data():
    """Load, validate, and clean the retail sales dataset."""
    if not DATA_FILE.exists():
        st.error(
            f"❌ Dataset not found: '{DATA_FILE.name}'. "
            "Please ensure the Excel file is placed in the same directory as app.py."
        )
        st.stop()

    try:
        df = pd.read_excel(DATA_FILE, engine="openpyxl")
    except Exception as exc:
        st.error(f"❌ Failed to load '{DATA_FILE.name}'. Error: {exc}")
        st.stop()

    # 1. Strip whitespace from column headers
    df.columns = [str(col).strip() for col in df.columns]

    # 2. Drop empty artifact columns present in source Excel
    columns_to_drop = ["Status", "unnamed1", "Unnamed: 14"]
    existing_drops = [col for col in columns_to_drop if col in df.columns]
    if existing_drops:
        df = df.drop(columns=existing_drops)

    # 3. Standardize column names
    rename_map = {
        "Occupation": "Sector",
        "Age Group": "Age_Group",
        "Product Category": "Product_Category",
    }
    df = df.rename(columns=rename_map)

    # 4. Required columns validation
    required_columns = {
        "User_ID",
        "Gender",
        "Age_Group",
        "State",
        "Zone",
        "Sector",
        "Product_Category",
        "Orders",
        "Amount",
        "Marital_Status",
    }
    missing_cols = sorted(required_columns - set(df.columns))
    if missing_cols:
        st.error("❌ Missing required columns: " + ", ".join(missing_cols))
        st.stop()

    # 5. Remove completely empty rows
    df = df.dropna(how="all").reset_index(drop=True)

    # 6. Clean text columns, normalize multi-spaces and non-breaking spaces
    text_columns = [
        "Gender",
        "Age_Group",
        "State",
        "Zone",
        "Sector",
        "Product_Category",
    ]
    for col in text_columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    # 7. Normalize Sector typo if any leading character was stripped
    df["Sector"] = df["Sector"].replace({"extile": "Textile"})

    # 8. Standardize Gender representation
    df["Gender"] = df["Gender"].str.upper().str.strip()

    # 9. Standardize Marital Status (0 -> Single, 1 -> Married)
    marital_map = {
        1: "Married",
        0: "Single",
        1.0: "Married",
        0.0: "Single",
        "1": "Married",
        "0": "Single",
        "1.0": "Married",
        "0.0": "Single",
        "Married": "Married",
        "married": "Married",
        "Single": "Single",
        "single": "Single",
    }
    df["Marital_Status"] = (
        df["Marital_Status"]
        .replace(marital_map)
        .astype("string")
        .str.strip()
    )

    # 10. Handle numeric columns & convert invalid/missing numeric values to 0
    for col in ["Orders", "Amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


# Load clean dataset
df = load_data()


# ============================================================
# 🎛️ 4. SIDEBAR FILTERS & SESSION STATE
# ============================================================

st.sidebar.title("🎛️ Dashboard Filters")

if st.sidebar.button("🔄 Reset Filters", width="stretch"):
    st.session_state.clear()
    st.rerun()

dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=True)

# --- 1. Zone Filter ---
zones = sorted(df["Zone"].dropna().unique().tolist())
if "zone_filter" not in st.session_state:
    st.session_state["zone_filter"] = zones

selected_zones = st.sidebar.multiselect(
    "📍 Zone",
    options=zones,
    key="zone_filter",
)

# --- 2. Dynamic State Filter (Cascading based on selected Zones) ---
if selected_zones:
    available_states = sorted(
        df.loc[df["Zone"].isin(selected_zones), "State"].dropna().unique().tolist()
    )
else:
    available_states = []

if "state_filter" not in st.session_state:
    st.session_state["state_filter"] = available_states
else:
    # Retain only states that are still available in the selected zones
    st.session_state["state_filter"] = [
        s for s in st.session_state["state_filter"] if s in available_states
    ]

selected_states = st.sidebar.multiselect(
    "🏛️ State",
    options=available_states,
    key="state_filter",
)

# --- 3. Age Group Filter ---
age_order = ["0-17", "18-25", "26-35", "36-45", "46-50", "51-55", "55+"]
available_ages = set(df["Age_Group"].dropna().unique())
age_options = [age for age in age_order if age in available_ages]
extra_ages = sorted(available_ages - set(age_options))
age_options.extend(extra_ages)

if "age_filter" not in st.session_state:
    st.session_state["age_filter"] = age_options

selected_ages = st.sidebar.multiselect(
    "🎂 Age Group",
    options=age_options,
    key="age_filter",
)

# --- 4. Gender Filter ---
gender_options = sorted(df["Gender"].dropna().unique().tolist())
selected_gender = st.sidebar.radio(
    "⚧️ Gender",
    options=["All"] + gender_options,
    index=0,
    key="gender_filter",
)

# --- 5. Marital Status Filter ---
marital_options = sorted(df["Marital_Status"].dropna().unique().tolist())
if "marital_filter" not in st.session_state:
    st.session_state["marital_filter"] = marital_options

selected_marital = st.sidebar.multiselect(
    "💍 Marital Status",
    options=marital_options,
    key="marital_filter",
)


# ============================================================
# 🎯 5. FILTER APPLICATION
# ============================================================

filtered = df.copy()

if selected_zones:
    filtered = filtered[filtered["Zone"].isin(selected_zones)]
else:
    filtered = filtered.iloc[0:0]

if selected_states:
    filtered = filtered[filtered["State"].isin(selected_states)]
else:
    filtered = filtered.iloc[0:0]

if selected_ages:
    filtered = filtered[filtered["Age_Group"].isin(selected_ages)]
else:
    filtered = filtered.iloc[0:0]

if selected_gender != "All":
    filtered = filtered[filtered["Gender"] == selected_gender]

if selected_marital:
    filtered = filtered[filtered["Marital_Status"].isin(selected_marital)]
else:
    filtered = filtered.iloc[0:0]


# ============================================================
# 🎨 6. THEMING & HIGH-CONTRAST CARD STYLING
# ============================================================

template = "plotly_dark" if dark_mode else "plotly_white"

if dark_mode:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        section[data-testid="stSidebar"] {
            background-color: #161b22;
        }
        h1, h2, h3, h4 {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    card_bg = "#161b22"
    card_border = "#30363d"
    title_color = "#8b949e"
    value_color = "#ffffff"
else:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #ffffff;
            color: #111827;
        }
        section[data-testid="stSidebar"] {
            background-color: #f6f8fa;
        }
        h1, h2, h3, h4 {
            color: #111827 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    card_bg = "#f6f8fa"
    card_border = "#d0d7de"
    title_color = "#57606a"
    value_color = "#111827"


# ============================================================
# 🏷️ 7. HEADER
# ============================================================

st.title("📊 Sales Data Analysis Dashboard")
st.caption("Interactive Retail Sales, Customer & Product Analysis")


# ============================================================
# 💳 8. KPI METRIC CARDS
# ============================================================

revenue = float(filtered["Amount"].sum())
orders = int(filtered["Orders"].sum())
customers = int(filtered["User_ID"].nunique())
aov = revenue / orders if orders > 0 else 0.0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

def render_kpi_card(column, icon, title, value):
    """Renders high-contrast HTML KPI cards compatible with Dark and Light mode."""
    with column:
        st.markdown(
            f"""
            <div style="
                background-color: {card_bg};
                border: 1px solid {card_border};
                border-radius: 10px;
                padding: 16px 20px;
                margin-bottom: 12px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            ">
                <div style="color: {title_color}; font-size: 13px; font-weight: 600; margin-bottom: 6px;">
                    {icon} {title}
                </div>
                <div style="color: {value_color}; font-size: 24px; font-weight: 700; line-height: 1.2;">
                    {value}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

render_kpi_card(kpi1, "💰", "Total Revenue", f"₹{revenue:,.2f}")
render_kpi_card(kpi2, "📦", "Total Orders", f"{orders:,}")
render_kpi_card(kpi3, "👥", "Unique Customers", f"{customers:,}")
render_kpi_card(kpi4, "🧾", "Average Order Value", f"₹{aov:,.2f}")

st.divider()


# ============================================================
# 📈 9. VISUALIZATIONS
# ============================================================

if filtered.empty:
    st.warning("⚠️ No data matches the selected filters. Please adjust your selections in the sidebar.")
else:
    # --------------------------------------------------------
    # 1. AGE GROUP & GENDER ANALYSIS
    # --------------------------------------------------------
    st.subheader("👥 Age Group & Gender Analysis")
    left, right = st.columns(2)

    age_gender = (
        filtered.groupby(["Age_Group", "Gender"], as_index=False)
        .agg(
            Count=("User_ID", "count"),
            Amount=("Amount", "sum"),
        )
    )

    gender_colors = {"M": "#1565C0", "F": "#90CAF9"}

    fig1 = px.bar(
        age_gender,
        x="Age_Group",
        y="Count",
        color="Gender",
        barmode="group",
        category_orders={"Age_Group": age_order},
        color_discrete_map=gender_colors,
        title="Record Count by Age Group & Gender",
        template=template,
    )
    fig1.update_layout(xaxis_title="Age Group", yaxis_title="Record Count", legend_title="Gender")
    left.plotly_chart(fig1, width="stretch")

    fig2 = px.bar(
        age_gender,
        x="Age_Group",
        y="Amount",
        color="Gender",
        barmode="group",
        category_orders={"Age_Group": age_order},
        color_discrete_map=gender_colors,
        title="Total Revenue (₹) by Age Group & Gender",
        template=template,
    )
    fig2.update_layout(xaxis_title="Age Group", yaxis_title="Amount (₹)", legend_title="Gender")
    right.plotly_chart(fig2, width="stretch")

    st.divider()

    # --------------------------------------------------------
    # 2. ZONE & MARITAL STATUS CONTRIBUTION
    # --------------------------------------------------------
    st.subheader("📍 Zone & Marital Status")
    left, right = st.columns(2)

    zone_data = (
        filtered.groupby("Zone", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )

    fig3 = px.pie(
        zone_data,
        names="Zone",
        values="Amount",
        hole=0.45,
        title="Zone-wise Revenue Contribution",
        template=template,
    )
    fig3.update_traces(textposition="inside", textinfo="percent")
    left.plotly_chart(fig3, width="stretch")

    marital_data = (
        filtered.groupby("Marital_Status", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )

    fig4 = px.pie(
        marital_data,
        names="Marital_Status",
        values="Amount",
        hole=0.45,
        title="Marital Status Revenue Contribution",
        template=template,
    )
    fig4.update_traces(textposition="inside", textinfo="percent")
    right.plotly_chart(fig4, width="stretch")

    st.divider()

    # --------------------------------------------------------
    # 3. SECTOR PERFORMANCE (HORIZONTAL BAR CHARTS)
    # --------------------------------------------------------
    st.subheader("🏢 Sector Performance")
    left, right = st.columns(2)

    sector_data = (
        filtered.groupby("Sector")
        .agg(
            Total_Orders=("Orders", "sum"),
            Average_Orders=("Orders", "mean"),
            Total_Amount=("Amount", "sum"),
        )
        .reset_index()
    )

    sector_total_orders = sector_data.sort_values("Total_Orders", ascending=False)

    fig5 = px.bar(
        sector_total_orders,
        x="Total_Orders",
        y="Sector",
        orientation="h",
        title="Sector-wise Total Orders",
        template=template,
    )
    fig5.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Total Orders",
        yaxis_title="Sector",
    )
    left.plotly_chart(fig5, width="stretch")

    sector_average_orders = sector_data.sort_values("Average_Orders", ascending=False)

    fig6 = px.bar(
        sector_average_orders,
        x="Average_Orders",
        y="Sector",
        orientation="h",
        title="Sector-wise Average Orders per Record",
        template=template,
    )
    fig6.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Average Orders",
        yaxis_title="Sector",
    )
    right.plotly_chart(fig6, width="stretch")

    st.divider()

    # --------------------------------------------------------
    # 4. TOP STATES & PRODUCT CATEGORIES
    # --------------------------------------------------------
    st.subheader("🏆 Top States & Product Categories")
    left, right = st.columns(2)

    top_states = (
        filtered.groupby("State", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
        .head(10)
    )

    fig7 = px.bar(
        top_states,
        x="Amount",
        y="State",
        orientation="h",
        title="Top 10 States by Revenue (₹)",
        template=template,
    )
    fig7.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Amount (₹)",
        yaxis_title="State",
    )
    left.plotly_chart(fig7, width="stretch")

    top_products_rev = (
        filtered.groupby("Product_Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
        .head(10)
    )

    fig8 = px.bar(
        top_products_rev,
        x="Amount",
        y="Product_Category",
        orientation="h",
        title="Top 10 Product Categories by Revenue (₹)",
        template=template,
    )
    fig8.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Amount (₹)",
        yaxis_title="Product Category",
    )
    right.plotly_chart(fig8, width="stretch")

    st.divider()

    # --------------------------------------------------------
    # 5. PRODUCT CATEGORY ORDERS (HORIZONTAL BAR CHARTS)
    # --------------------------------------------------------
    st.subheader("🛍️ Product Category Orders")
    left, right = st.columns(2)

    product_orders = (
        filtered.groupby("Product_Category")
        .agg(
            Total_Orders=("Orders", "sum"),
            Average_Orders=("Orders", "mean"),
        )
        .reset_index()
    )

    product_total_orders = product_orders.sort_values("Total_Orders", ascending=False).head(10)

    fig9 = px.bar(
        product_total_orders,
        x="Total_Orders",
        y="Product_Category",
        orientation="h",
        title="Top 10 Categories by Total Orders",
        template=template,
    )
    fig9.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Total Orders",
        yaxis_title="Product Category",
    )
    left.plotly_chart(fig9, width="stretch")

    product_average_orders = product_orders.sort_values("Average_Orders", ascending=False).head(10)

    fig10 = px.bar(
        product_average_orders,
        x="Average_Orders",
        y="Product_Category",
        orientation="h",
        title="Top 10 Categories by Average Orders",
        template=template,
    )
    fig10.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Average Orders",
        yaxis_title="Product Category",
    )
    right.plotly_chart(fig10, width="stretch")

    st.divider()

    # --------------------------------------------------------
    # 6. SECTOR TOTAL REVENUE (HORIZONTAL BAR CHART)
    # --------------------------------------------------------
    st.subheader("💰 Sector-wise Total Revenue")

    sector_amount = (
        filtered.groupby("Sector", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )

    fig11 = px.bar(
        sector_amount,
        x="Amount",
        y="Sector",
        orientation="h",
        title="Sector-wise Total Revenue (₹)",
        template=template,
    )
    fig11.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Amount (₹)",
        yaxis_title="Sector",
    )
    st.plotly_chart(fig11, width="stretch")

    st.divider()

    # --------------------------------------------------------
    # 7. FILTERED RAW DATA & CSV EXPORT
    # --------------------------------------------------------
    st.subheader("📋 Filtered Data")

    with st.expander("Show Raw Data"):
        st.dataframe(filtered, width="stretch", hide_index=True)
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered CSV",
            data=csv,
            file_name="sales_filtered.csv",
            mime="text/csv",
            width="stretch",
        )


# ============================================================
# 📄 10. FOOTER
# ============================================================

st.divider()
st.caption("Sales Data Analysis Dashboard • Built with Streamlit, Pandas & Plotly")
