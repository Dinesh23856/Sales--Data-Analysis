from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sales Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DATA FILE PATH
# ============================================================

DATA_FILE = Path(__file__).resolve().parent / "project Data new.xlsx"

# ============================================================
# LOAD AND CLEAN DATA
# ============================================================

@st.cache_data
def load_data():
    """Load and clean the sales dataset."""
    if not DATA_FILE.exists():
        st.error(
            f"Dataset not found: '{DATA_FILE.name}'. "
            "Make sure the Excel file is in the same folder as app.py."
        )
        st.stop()

    try:
        df = pd.read_excel(DATA_FILE, engine="openpyxl")
    except Exception as exc:
        st.error(f"Could not read '{DATA_FILE.name}'. Error: {exc}")
        st.stop()

    # Clean column headers
    df.columns = [str(col).strip() for col in df.columns]

    # Drop redundant columns
    columns_to_drop = ["Status", "unnamed1", "Unnamed: 14"]
    existing_drop_columns = [col for col in columns_to_drop if col in df.columns]
    if existing_drop_columns:
        df = df.drop(columns=existing_drop_columns)

    # Standardize column headers
    rename_map = {
        "Occupation": "Sector",
        "Age Group": "Age_Group",
        "Product Category": "Product_Category",
    }
    df = df.rename(columns=rename_map)

    # Schema validation
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
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        st.error(
            "The dataset is missing these required columns: "
            + ", ".join(missing_columns)
        )
        st.stop()

    # Drop blank rows
    df = df.dropna(how="all").reset_index(drop=True)

    # Clean text columns
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

    # Standardize Gender
    df["Gender"] = df["Gender"].str.upper().str.strip()

    # Standardize Marital Status
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

    # Numeric conversion
    for col in ["Orders", "Amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

df = load_data()

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("🎛️ Dashboard Filters")

if st.sidebar.button("🔄 Reset Filters", use_container_width=True):
    st.session_state.clear()
    st.rerun()

dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=True)

# 1. Zone Filter
zones = sorted(df["Zone"].dropna().unique().tolist())
selected_zones = st.sidebar.multiselect("Zone", options=zones, default=zones, key="zone_filter")

# 2. State Filter (Cascading)
if selected_zones:
    state_options = sorted(
        df.loc[df["Zone"].isin(selected_zones), "State"]
        .dropna()
        .unique()
        .tolist()
    )
else:
    state_options = []

selected_states = st.sidebar.multiselect("State", options=state_options, default=state_options, key="state_filter")

# 3. Age Group Filter
age_order = ["0-17", "18-25", "26-35", "36-45", "46-50", "51-55", "55+"]
available_ages = set(df["Age_Group"].dropna().unique())
age_options = [age for age in age_order if age in available_ages]
extra_ages = sorted(available_ages - set(age_options))
age_options.extend(extra_ages)

selected_ages = st.sidebar.multiselect("Age Group", options=age_options, default=age_options, key="age_filter")

# 4. Gender Filter
gender_options = sorted(df["Gender"].dropna().unique().tolist())
selected_gender = st.sidebar.radio("Gender", options=["All"] + gender_options, index=0, key="gender_filter")

# 5. Marital Status Filter
marital_options = sorted(df["Marital_Status"].dropna().unique().tolist())
selected_marital = st.sidebar.multiselect("Marital Status", options=marital_options, default=marital_options, key="marital_filter")

# ============================================================
# APPLY FILTER LOGIC
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
# THEME STYLING
# ============================================================

template = "plotly_dark" if dark_mode else "plotly_white"

if dark_mode:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        section[data-testid="stSidebar"] { background-color: #161b22; }
        h1, h2, h3, h4 { color: #ffffff !important; }
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
        .stApp { background-color: #ffffff; color: #111827; }
        h1, h2, h3, h4 { color: #111827 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    card_bg = "#f6f8fa"
    card_border = "#d0d7de"
    title_color = "#57606a"
    value_color = "#24292f"

# ============================================================
# HEADER & KPIS
# ============================================================

st.title("📊 Sales Data Analysis Dashboard")
st.caption("Interactive Retail Sales Performance & Demographic Analysis")

revenue = filtered["Amount"].sum()
orders = filtered["Orders"].sum()
customers = filtered["User_ID"].nunique()
aov = revenue / orders if orders > 0 else 0.0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

def render_kpi_card(column, icon, title, value):
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
                <div style="color: {title_color}; font-size: 14px; font-weight: 600; margin-bottom: 8px;">
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
render_kpi_card(kpi2, "📦", "Total Orders", f"{int(orders):,}")
render_kpi_card(kpi3, "👥", "Unique Customers", f"{customers:,}")
render_kpi_card(kpi4, "🧾", "Average Order Value", f"₹{aov:,.2f}")

st.divider()

# ============================================================
# CHARTS SECTION
# ============================================================

if filtered.empty:
    st.warning("⚠️ No data matches the selected filters. Please adjust your selections in the sidebar.")
else:
    # 1. Age Group & Gender
    st.subheader("👥 Age Group & Gender Analysis")
    left, right = st.columns(2)

    age_gender = (
        filtered.groupby(["Age_Group", "Gender"], as_index=False)
        .agg(Orders=("Orders", "sum"), Amount=("Amount", "sum"))
    )
    gender_colors = {"M": "#1565C0", "F": "#90CAF9"}

    fig1 = px.bar(
        age_gender,
        x="Age_Group",
        y="Orders",
        color="Gender",
        barmode="group",
        category_orders={"Age_Group": age_order},
        color_discrete_map=gender_colors,
        title="Total Orders by Age Group & Gender",
        template=template,
    )
    fig1.update_layout(xaxis_title="Age Group", yaxis_title="Orders", legend_title="Gender")
    left.plotly_chart(fig1, use_container_width=True)

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
    right.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # 2. Zone & Marital Status
    st.subheader("📍 Zone & Marital Status Analysis")
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
    left.plotly_chart(fig3, use_container_width=True)

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
    right.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # 3. Sector Performance
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
        x="Sector",
        y="Total_Orders",
        title="Sector-wise Total Orders",
        template=template,
    )
    fig5.update_layout(xaxis_title="Sector", yaxis_title="Total Orders", xaxis_tickangle=-45)
    left.plotly_chart(fig5, use_container_width=True)

    sector_average_orders = sector_data.sort_values("Average_Orders", ascending=False)
    fig6 = px.bar(
        sector_average_orders,
        x="Sector",
        y="Average_Orders",
        title="Sector-wise Average Orders per Record",
        template=template,
    )
    fig6.update_layout(xaxis_title="Sector", yaxis_title="Average Orders", xaxis_tickangle=-45)
    right.plotly_chart(fig6, use_container_width=True)

    st.divider()

    # 4. Top States & Categories by Revenue
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
    fig7.update_layout(yaxis=dict(autorange="reversed"), xaxis_title="Amount (₹)", yaxis_title="State")
    left.plotly_chart(fig7, use_container_width=True)

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
    fig8.update_layout(yaxis=dict(autorange="reversed"), xaxis_title="Amount (₹)", yaxis_title="Product Category")
    right.plotly_chart(fig8, use_container_width=True)

    st.divider()

    # 5. Product Category Orders
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
        x="Product_Category",
        y="Total_Orders",
        title="Top 10 Categories by Total Orders",
        template=template,
    )
    fig9.update_layout(xaxis_title="Product Category", yaxis_title="Total Orders", xaxis_tickangle=-45)
    left.plotly_chart(fig9, use_container_width=True)

    product_average_orders = product_orders.sort_values("Average_Orders", ascending=False).head(10)
    fig10 = px.bar(
        product_average_orders,
        x="Product_Category",
        y="Average_Orders",
        title="Top 10 Categories by Average Orders",
        template=template,
    )
    fig10.update_layout(xaxis_title="Product Category", yaxis_title="Average Orders", xaxis_tickangle=-45)
    right.plotly_chart(fig10, use_container_width=True)

    st.divider()

    # 6. Sector Revenue
    st.subheader("💰 Sector-wise Total Revenue")
    sector_amount = (
        filtered.groupby("Sector", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )
    fig11 = px.bar(
        sector_amount,
        x="Sector",
        y="Amount",
        title="Sector-wise Total Revenue (₹)",
        template=template,
    )
    fig11.update_layout(xaxis_title="Sector", yaxis_title="Amount (₹)", xaxis_tickangle=-45)
    st.plotly_chart(fig11, use_container_width=True)

    st.divider()

    # 7. Raw Data & Export
    st.subheader("📋 Filtered Data")
    with st.expander("Show Raw Data"):
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered CSV",
            data=csv,
            file_name="sales_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("Sales Data Analysis Dashboard • Built with Streamlit, Pandas & Plotly")
