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

DATA_FILE = (
    Path(__file__).resolve().parent
    / "project Data new.xlsx"
)


# ============================================================
# LOAD AND CLEAN DATA
# ============================================================

@st.cache_data
def load_data():
    """Load and clean the sales dataset."""

    # --------------------------------------------------------
    # Check dataset
    # --------------------------------------------------------

    if not DATA_FILE.exists():
        st.error(
            f"Dataset not found: '{DATA_FILE.name}'. "
            "Make sure the Excel file is in the same folder as app.py."
        )
        st.stop()

    # --------------------------------------------------------
    # Read Excel file
    # --------------------------------------------------------

    try:
        df = pd.read_excel(
            DATA_FILE,
            engine="openpyxl",
        )

    except Exception as exc:
        st.error(
            f"Could not read '{DATA_FILE.name}'. Error: {exc}"
        )
        st.stop()

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # --------------------------------------------------------
    # Remove unnecessary columns
    # --------------------------------------------------------

    columns_to_drop = [
        "Status",
        "unnamed1",
        "Unnamed: 14",
    ]

    existing_drop_columns = [
        column
        for column in columns_to_drop
        if column in df.columns
    ]

    if existing_drop_columns:
        df = df.drop(
            columns=existing_drop_columns
        )

    # --------------------------------------------------------
    # Standardize column names
    # --------------------------------------------------------

    rename_map = {
        "Occupation": "Sector",
        "Age Group": "Age_Group",
        "Product Category": "Product_Category",
    }

    df = df.rename(
        columns=rename_map
    )

    # --------------------------------------------------------
    # Required columns
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
            "The dataset is missing these required columns: "
            + ", ".join(missing_columns)
        )
        st.stop()

    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    df = (
        df
        .dropna(how="all")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Clean text columns
    # --------------------------------------------------------

    text_columns = [
        "Gender",
        "Age_Group",
        "State",
        "Zone",
        "Sector",
        "Product_Category",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # Clean Marital Status
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Convert numeric columns
    # --------------------------------------------------------

    for column in ["Orders", "Amount"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        ).fillna(0)

    return df


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎛️ Dashboard Filters")


# ============================================================
# RESET FILTERS
# ============================================================

if st.sidebar.button(
    "🔄 Reset Filters",
    use_container_width=True,
):
    st.session_state.clear()
    st.rerun()


# ============================================================
# DARK MODE
# ============================================================

dark_mode = st.sidebar.checkbox(
    "🌙 Dark Mode",
    value=True,
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
    options=zones,
    default=zones,
)


# ============================================================
# STATE FILTER
# ============================================================

if selected_zones:

    state_options = sorted(
        df.loc[
            df["Zone"].isin(selected_zones),
            "State",
        ]
        .dropna()
        .unique()
        .tolist()
    )

else:

    state_options = []


selected_states = st.sidebar.multiselect(
    "State",
    options=state_options,
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
    .unique()
)

age_options = [
    age
    for age in age_order
    if age in available_ages
]

extra_ages = sorted(
    available_ages - set(age_options)
)

age_options.extend(extra_ages)


selected_ages = st.sidebar.multiselect(
    "Age Group",
    options=age_options,
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
    options=["All"] + gender_options,
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
    options=marital_options,
    default=marital_options,
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()


# ------------------------------------------------------------
# Zone
# ------------------------------------------------------------

if selected_zones:

    filtered = filtered[
        filtered["Zone"].isin(selected_zones)
    ]

else:

    filtered = filtered.iloc[0:0]


# ------------------------------------------------------------
# State
# ------------------------------------------------------------

if selected_states:

    filtered = filtered[
        filtered["State"].isin(selected_states)
    ]

else:

    filtered = filtered.iloc[0:0]


# ------------------------------------------------------------
# Age Group
# ------------------------------------------------------------

if selected_ages:

    filtered = filtered[
        filtered["Age_Group"].isin(selected_ages)
    ]

else:

    filtered = filtered.iloc[0:0]


# ------------------------------------------------------------
# Gender
# ------------------------------------------------------------

if selected_gender != "All":

    filtered = filtered[
        filtered["Gender"] == selected_gender
    ]


# ------------------------------------------------------------
# Marital Status
# ------------------------------------------------------------

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


# ============================================================
# CUSTOM CSS
# ============================================================

if dark_mode:

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #0e1117;
        }

        section[data-testid="stSidebar"] {
            background-color: #161b22;
        }

        h1, h2, h3 {
            color: #ffffff !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #ffffff;
        }

        h1, h2, h3 {
            color: #111827 !important;
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
# KPI CALCULATIONS
# ============================================================

revenue = filtered["Amount"].sum()

orders = filtered["Orders"].sum()

customers = filtered["User_ID"].nunique()

aov = (
    revenue / orders
    if orders > 0
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


if dark_mode:

    card_bg = "#161b22"
    card_border = "#30363d"
    title_color = "#c9d1d9"
    value_color = "#ffffff"

else:

    card_bg = "#f8f9fa"
    card_border = "#e5e7eb"
    title_color = "#374151"
    value_color = "#111827"


def kpi_card(
    column,
    icon,
    title,
    value,
):
    """Display a custom KPI card."""

    with column:

        st.markdown(
            f"""
            <div style="
                background-color: {card_bg};
                border: 1px solid {card_border};
                border-radius: 12px;
                padding: 18px;
                min-height: 110px;
                box-sizing: border-box;
                margin-bottom: 10px;
            ">

                <div style="
                    color: {title_color};
                    font-size: 15px;
                    font-weight: 600;
                    margin-bottom: 10px;
                ">
                    {icon} {title}
                </div>

                <div style="
                    color: {value_color};
                    font-size: 25px;
                    font-weight: 700;
                    line-height: 1.2;
                ">
                    {value}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


kpi_card(
    kpi1,
    "💰",
    "Total Revenue",
    f"₹{revenue:,.2f}",
)

kpi_card(
    kpi2,
    "📦",
    "Total Orders",
    f"{int(orders):,}",
)

kpi_card(
    kpi3,
    "👥",
    "Unique Customers",
    f"{customers:,}",
)

kpi_card(
    kpi4,
    "🧾",
    "Average Order Value",
    f"₹{aov:,.2f}",
)


st.divider()


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "⚠️ No data matches the selected filters. "
        "Please adjust your selections in the sidebar."
    )

else:

    # ========================================================
    # 1. AGE GROUP & GENDER
    # ========================================================

    st.subheader(
        "👥 Age Group & Gender Analysis"
    )

    left, right = st.columns(2)


    age_gender = (
        filtered
        .groupby(
            ["Age_Group", "Gender"],
            as_index=False,
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
    # Total Orders by Age Group & Gender
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
        title="Total Orders by Age Group & Gender",
        template=template,
    )

    fig1.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Orders",
        legend_title="Gender",
    )

    left.plotly_chart(
        fig1,
        use_container_width=True,
    )


    # --------------------------------------------------------
    # Total Revenue by Age Group & Gender
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
        title="Total Revenue (₹) by Age Group & Gender",
        template=template,
    )

    fig2.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Amount (₹)",
        legend_title="Gender",
    )

    right.plotly_chart(
        fig2,
        use_container_width=True,
    )


    st.divider()


    # ========================================================
    # 2. ZONE & MARITAL STATUS
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
            as_index=False,
        )["Amount"]
        .sum()
        .sort_values(
            "Amount",
            ascending=False,
        )
    )


    fig3 = px.pie(
        zone_data,
        names="Zone",
        values="Amount",
        hole=0.45,
        title="Zone-wise Revenue Contribution",
        template=template,
    )

    fig3.update_traces(
        textposition="inside",
        textinfo="percent",
    )


    left.plotly_chart(
        fig3,
        use_container_width=True,
    )


    # --------------------------------------------------------
    # Marital Status Revenue
    # --------------------------------------------------------

    marital_data = (
        filtered
        .groupby(
            "Marital_Status",
            as_index=False,
        )["Amount"]
        .sum()
        .sort_values(
            "Amount",
            ascending=False,
        )
    )


    fig4 = px.pie(
        marital_data,
        names="Marital_Status",
        values="Amount",
        hole=0.45,
        title="Marital Status Revenue Contribution",
        template=template,
    )

    fig4.update_traces(
        textposition="inside",
        textinfo="percent",
    )


    right.plotly_chart(
        fig4,
        use_container_width=True,
    )


    st.divider()


    # ========================================================
    # 3. SECTOR PERFORMANCE
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
    )


    # --------------------------------------------------------
    # Sector Total Orders
    # --------------------------------------------------------

    sector_total_orders = (
        sector_data
        .sort_values(
            "Total_Orders",
            ascending=False,
        )
    )


    fig5 = px.bar(
        sector_total_orders,
        x="Sector",
        y="Total_Orders",
        title="Sector-wise Total Orders",
        template=template,
    )

    fig5.update_layout(
        xaxis_title="Sector",
        yaxis_title="Total Orders",
        xaxis_tickangle=-45,
    )


    left.plotly_chart(
        fig5,
        use_container_width=True,
    )


    # --------------------------------------------------------
    # Sector Average Orders
    # --------------------------------------------------------

    sector_average_orders = (
        sector_data
        .sort_values(
            "Average_Orders",
            ascending=False,
        )
    )


    fig6 = px.bar(
        sector_average_orders,
        x="Sector",
        y="Average_Orders",
        title="Sector-wise Average Orders per Record",
        template=template,
    )

    fig6.update_layout(
        xaxis_title="Sector",
        yaxis_title="Average Orders",
        xaxis_tickangle=-45,
    )


    right.plotly_chart(
        fig6,
        use_container_width=True,
    )


    st.divider()


    # ========================================================
    # 4. TOP STATES & PRODUCT CATEGORIES
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
            as_index=False,
        )["Amount"]
        .sum()
        .sort_values(
            "Amount",
            ascending=False,
        )
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
        yaxis=dict(
            autorange="reversed"
        ),
        xaxis_title="Amount (₹)",
        yaxis_title="State",
    )


    left.plotly_chart(
        fig7,
        use_container_width=True,
    )


    # --------------------------------------------------------
    # Top 10 Product Categories
    # --------------------------