from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATA FILE
# ============================================================

DATA_FILE = Path(__file__).parent / "project Data new.xlsx"


# ============================================================
# LOAD AND CLEAN DATA
# ============================================================

@st.cache_data
def load_data():
    """Load and clean the sales dataset."""

    if not DATA_FILE.exists():
        st.error(
            f"Dataset not found: {DATA_FILE.name}. "
            "Make sure the Excel file is uploaded to the same repository "
            "folder as app.py."
        )
        st.stop()

    try:
        df = pd.read_excel(
            DATA_FILE,
            engine="openpyxl"
        )
    except Exception as exc:
        st.error(
            f"Could not read {DATA_FILE.name}: {exc}"
        )
        st.stop()

    # Clean column names
    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # Rename columns
    rename_map = {
        "Occupation": "Sector",
        "Age Group": "Age_Group",
        "Product Category": "Product_Category",
    }

    df = df.rename(
        columns=rename_map
    )

    # --------------------------------------------------------
    # Marital Status Cleaning
    # --------------------------------------------------------

    if "Marital_Status" in df.columns:

        df["Marital_Status"] = (
            df["Marital_Status"]
            .astype(str)
            .str.strip()
            .replace(
                {
                    "1": "Married",
                    "0": "Single",
                    "1.0": "Married",
                    "0.0": "Single",
                }
            )
        )

    # --------------------------------------------------------
    # Numeric Columns
    # --------------------------------------------------------

    for col in ["Orders", "Amount"]:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

    # --------------------------------------------------------
    # Required Columns Check
    # --------------------------------------------------------

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

    missing_columns = sorted(
        required_columns - set(df.columns)
    )

    if missing_columns:

        st.error(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

        st.stop()

    return df


# Load dataset
df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎛️ Dashboard Filters")


# ------------------------------------------------------------
# Reset Filters
# ------------------------------------------------------------

if st.sidebar.button("🔄 Reset Filters"):

    st.session_state.clear()

    st.rerun()


# ------------------------------------------------------------
# Dark Mode
# ------------------------------------------------------------

dark_mode = st.sidebar.checkbox(
    "🌙 Dark Mode",
    value=False
)


# ============================================================
# ZONE FILTER
# ============================================================

zones = sorted(
    df["Zone"]
    .dropna()
    .unique()
    .tolist()
)

selected_zones = st.sidebar.multiselect(
    "Zone",
    zones,
    default=zones,
)


# ============================================================
# STATE FILTER
# ============================================================

if selected_zones:

    state_options = sorted(
        df.loc[
            df["Zone"].isin(selected_zones),
            "State"
        ]
        .dropna()
        .unique()
        .tolist()
    )

else:

    state_options = []


selected_states = st.sidebar.multiselect(
    "State",
    state_options,
    default=state_options,
)


# ============================================================
# AGE GROUP FILTER
# ============================================================

age_order = [
    "0-17",
    "18-25",
    "26-35",
    "36-45",
    "46-50",
    "51-55",
    "55+",
]


available_ages = set(
    df["Age_Group"]
    .dropna()
    .astype(str)
    .unique()
)


age_options = [
    age
    for age in age_order
    if age in available_ages
]


# Include unexpected age groups if they exist
age_options += sorted(
    available_ages - set(age_options)
)


selected_ages = st.sidebar.multiselect(
    "Age Group",
    age_options,
    default=age_options,
)


# ============================================================
# GENDER FILTER
# ============================================================

gender_options = sorted(
    df["Gender"]
    .dropna()
    .unique()
    .tolist()
)


selected_gender = st.sidebar.radio(
    "Gender",
    ["All"] + gender_options,
    index=0,
)


# ============================================================
# MARITAL STATUS FILTER
# ============================================================

marital_options = sorted(
    df["Marital_Status"]
    .dropna()
    .unique()
    .tolist()
)


selected_marital = st.sidebar.multiselect(
    "Marital Status",
    marital_options,
    default=marital_options,
)


# ============================================================
# FILTER DATA
# ============================================================

filtered = df.copy()


# Zone
if selected_zones:

    filtered = filtered[
        filtered["Zone"].isin(
            selected_zones
        )
    ]

else:

    filtered = filtered.iloc[0:0]


# State
if selected_states:

    filtered = filtered[
        filtered["State"].isin(
            selected_states
        )
    ]


# Age Group
if selected_ages:

    filtered = filtered[
        filtered["Age_Group"].isin(
            selected_ages
        )
    ]


# Gender
if selected_gender != "All":

    filtered = filtered[
        filtered["Gender"]
        == selected_gender
    ]


# Marital Status
if selected_marital:

    filtered = filtered[
        filtered["Marital_Status"].isin(
            selected_marital
        )
    ]

else:

    filtered = filtered.iloc[0:0]


# ============================================================
# THEME
# ============================================================

template = (
    "plotly_dark"
    if dark_mode
    else "plotly_white"
)


if dark_mode:

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #0e1117;
        }

        div[data-testid="stMetric"] {
            background-color: #161b22;
            border: 1px solid #30363d;
            padding: 15px;
            border-radius: 10px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <style>

        div[data-testid="stMetric"] {
            background-color: #f8f9fa;
            border: 1px solid #e5e7eb;
            padding: 15px;
            border-radius: 10px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 Sales Data Analysis Dashboard"
)

st.caption(
    "Interactive Retail Sales Dashboard"
)


# ============================================================
# KPI
# ============================================================

revenue = filtered["Amount"].sum()

orders = filtered["Orders"].sum()

customers = filtered["User_ID"].nunique()

aov = (
    revenue / orders
    if orders
    else 0
)


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "💰 Total Revenue",
    f"₹{revenue:,.2f}"
)


c2.metric(
    "📦 Total Orders",
    f"{int(orders):,}"
)


c3.metric(
    "👥 Unique Customers",
    f"{customers:,}"
)


c4.metric(
    "🧾 Average Order Value",
    f"₹{aov:,.2f}"
)


st.divider()


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "No data matches the selected filters. "
        "Please change the filters."
    )

else:

    # ========================================================
    # AGE GROUP & GENDER
    # ========================================================

    st.subheader(
        "👥 Age Group & Gender Analysis"
    )

    left, right = st.columns(2)


    age_gender = (
        filtered
        .groupby(
            ["Age_Group", "Gender"],
            as_index=False
        )
        .agg(
            Orders=("Orders", "sum"),
            Amount=("Amount", "sum"),
        )
    )


    gender_colors = {
        "M": "#1565C0",
        "F": "#90CAF9",
    }


    # --------------------------------------------------------
    # Orders by Age Group & Gender
    # --------------------------------------------------------

    fig1 = px.bar(
        age_gender,
        x="Age_Group",
        y="Orders",
        color="Gender",
        barmode="group",
        category_orders={
            "Age_Group": age_order
        },
        color_discrete_map=gender_colors,
        title="Orders by Age Group & Gender",
        template=template,
    )


    left.plotly_chart(
        fig1,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Amount by Age Group & Gender
    # --------------------------------------------------------

    fig2 = px.bar(
        age_gender,
        x="Age_Group",
        y="Amount",
        color="Gender",
        barmode="group",
        category_orders={
            "Age_Group": age_order
        },
        color_discrete_map=gender_colors,
        title="Amount by Age Group & Gender",
        template=template,
    )


    right.plotly_chart(
        fig2,
        use_container_width=True
    )


    st.divider()


    # ========================================================
    # ZONE & MARITAL STATUS
    # ========================================================

    st.subheader(
        "📍 Zone & Marital Status"
    )


    left, right = st.columns(2)


    # --------------------------------------------------------
    # Zone Revenue
    # --------------------------------------------------------

    zone_data = (
        filtered
        .groupby(
            "Zone",
            as_index=False
        )["Amount"]
        .sum()
        .sort_values(
            "Amount",
            ascending=False
        )
    )


    fig3 = px.pie(
        zone_data,
        names="Zone",
        values="Amount",
        hole=0.45,
        title="Zone-wise Revenue",
        template=template,
    )


    left.plotly_chart(
        fig3,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Marital Status Revenue
    # --------------------------------------------------------

    marital_data = (
        filtered
        .groupby(
            "Marital_Status",
            as_index=False
        )["Amount"]
        .sum()
    )


    fig4 = px.pie(
        marital_data,
        names="Marital_Status",
        values="Amount",
        hole=0.45,
        title="Marital Status Revenue",
        template=template,
    )


    right.plotly_chart(
        fig4,
        use_container_width=True
    )


    st.divider()


    # ========================================================
    # SECTOR PERFORMANCE
    # ========================================================

    st.subheader(
        "🏢 Sector Performance"
    )


    left, right = st.columns(2)


    sector_data = (
        filtered
        .groupby("Sector")
        .agg(
            Total_Orders=("Orders", "sum"),
            Average_Orders=("Orders", "mean"),
            Total_Amount=("Amount", "sum"),
        )
        .reset_index()
        .sort_values(
            "Total_Orders",
            ascending=False
        )
    )


    # --------------------------------------------------------
    # Sector Total Orders
    # --------------------------------------------------------

    fig5 = px.bar(
        sector_data,
        x="Sector",
        y="Total_Orders",
        title="Sector-wise Total Orders",
        template=template,
    )


    fig5.update_layout(
        xaxis_tickangle=-45
    )


    left.plotly_chart(
        fig5,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Sector Average Orders
    # --------------------------------------------------------

    fig6 = px.bar(
        sector_data.sort_values(
            "Average_Orders",
            ascending=False
        ),
        x="Sector",
        y="Average_Orders",
        title="Sector-wise Average Orders",
        template=template,
    )


    fig6.update_layout(
        xaxis_tickangle=-45
    )


    right.plotly_chart(
        fig6,
        use_container_width=True
    )


    st.divider()


    # ========================================================
    # TOP STATES & PRODUCT CATEGORIES
    # ========================================================

    st.subheader(
        "🏆 Top States & Product Categories"
    )


    left, right = st.columns(2)


    # --------------------------------------------------------
    # Top 10 States
    # --------------------------------------------------------

    top_states = (
        filtered
        .groupby(
            "State",
            as_index=False
        )["Amount"]
        .sum()
        .sort_values(
            "Amount",
            ascending=False
        )
        .head(10)
    )


    fig7 = px.bar(
        top_states,
        x="Amount",
        y="State",
        orientation="h",
        title="Top 10 States by Revenue",
        template=template,
    )


    fig7.update_layout(
        yaxis=dict(
            autorange="reversed"
        )
    )


    left.plotly_chart(
        fig7,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Top Product Categories
    # --------------------------------------------------------

    product_data = (
        filtered
        .groupby(
            "Product_Category",
            as_index=False
        )["Amount"]
        .sum()
        .sort_values(
            "Amount",
            ascending=False
        )
        .head(10)
    )


    fig8 = px.bar(
        product_data,
        x="Amount",
        y="Product_Category",
        orientation="h",
        title="Top 10 Product Categories by Revenue",
        template=template,
    )


    fig8.update_layout(
        yaxis=dict(
            autorange="reversed"
        )
    )


    right.plotly_chart(
        fig8,
        use_container_width=True
    )


    st.divider()


    # ========================================================
    # PRODUCT CATEGORY ORDERS
    # ========================================================

    st.subheader(
        "🛍️ Product Category Orders"
    )


    left, right = st.columns(2)


    product_orders = (
        filtered
        .groupby("Product_Category")
        .agg(
            Total_Orders=("Orders", "sum"),
            Average_Orders=("Orders", "mean"),
        )
        .reset_index()
    )


    # --------------------------------------------------------
    # Product Category Total Orders
    # --------------------------------------------------------

    product_total_orders = (
        product_orders
        .sort_values(
            "Total_Orders",
            ascending=False
        )
        .head(10)
    )


    fig9 = px.bar(
        product_total_orders,
        x="Product_Category",
        y="Total_Orders",
        title="Top 10 Product Categories by Total Orders",
        template=template,
    )


    fig9.update_layout(
        xaxis_tickangle=-45
    )


    left.plotly_chart(
        fig9,
        use_container_width=True
    )


    # --------------------------------------------------------
    # Product Category Average Orders
    # --------------------------------------------------------

    product_average_orders = (
        product_orders
        .sort_values(
            "Average_Orders",
            ascending=False
        )
        .head(10)
    )


    fig10 = px.bar(
        product_average_orders,
        x="Product_Category",
        y="Average_Orders",
        title="Top 10 Product Categories by Average Orders",
        template=template,
    )


    fig10.update_layout(
        xaxis_tickangle=-45
    )


    right.plotly_chart(
        fig10,
        use_container_width=True
    )


    st.divider()


    # ========================================================
    # SECTOR TOTAL AMOUNT
    # ========================================================

    st.subheader(
        "💰 Sector-wise Total Amount"
    )


    sector_amount = (
        filtered
        .groupby(
            "Sector",
            as_index=False
        )["Amount"]
        .sum()
        .sort_values(
            "Amount",
            ascending=False
        )
    )


    fig11 = px.bar(
        sector_amount,
        x="Sector",
        y="Amount",
        title="Sector-wise Total Revenue",
        template=template,
    )


    fig11.update_layout(
        xaxis_tickangle=-45
    )


    st.plotly_chart(
        fig11,
        use_container_width=True
    )


    st.divider()


    # ========================================================
    # RAW DATA
    # ========================================================

    st.subheader(
        "📋 Filtered Data"
    )


    with st.expander(
        "Show Raw Data"
    ):

        st.dataframe(
            filtered,
            use_container_width=True
        )


        csv = (
            filtered
            .to_csv(index=False)
            .encode("utf-8")
        )


        st.download_button(
            "⬇️ Download Filtered CSV",
            csv,
            "sales_filtered.csv",
            "text/csv",
        )


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Sales Data Analysis Dashboard • "
    "Built with Streamlit, Pandas & Plotly"
)