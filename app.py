from pathlib import Path
import io

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "project Data new.xlsx"


@st.cache_data
def load_data():
    path = Path(DATA_FILE)

    if not path.exists():
        st.error(f"Dataset not found: {DATA_FILE}")
        st.stop()

    df = pd.read_excel(path, engine="openpyxl")

    df.columns = [str(c).strip() for c in df.columns]

    if "Occupation" in df.columns and "Sector" not in df.columns:
        df = df.rename(columns={"Occupation": "Sector"})

    if "Age Group" in df.columns:
        df = df.rename(columns={"Age Group": "Age_Group"})

    if "Product Category" in df.columns:
        df = df.rename(columns={"Product Category": "Product_Category"})

    if "Marital_Status" in df.columns:
        df["Marital_Status"] = df["Marital_Status"].replace({
            1: "Married",
            0: "Single"
        })

    for col in ["Orders", "Amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_data()


# ---------------- SIDEBAR ----------------

st.sidebar.title("🎛️ Dashboard Filters")

dark_mode = st.sidebar.checkbox("🌙 Dark Mode")

zones = sorted(df["Zone"].dropna().unique()) if "Zone" in df.columns else []

selected_zones = st.sidebar.multiselect(
    "Zone",
    zones,
    default=zones
)

if selected_zones and "State" in df.columns:
    state_options = sorted(
        df[df["Zone"].isin(selected_zones)]["State"]
        .dropna()
        .unique()
    )
else:
    state_options = []

selected_states = st.sidebar.multiselect(
    "State",
    state_options,
    default=state_options
)


age_order = [
    "0-17",
    "18-25",
    "26-35",
    "36-45",
    "46-50",
    "51-55",
    "55+"
]

if "Age_Group" in df.columns:
    available_ages = set(df["Age_Group"].dropna().unique())
    age_options = [
        age for age in age_order
        if age in available_ages
    ]
else:
    age_options = []

selected_ages = st.sidebar.multiselect(
    "Age Group",
    age_options,
    default=age_options
)


gender_options = (
    sorted(df["Gender"].dropna().unique())
    if "Gender" in df.columns
    else []
)

selected_gender = st.sidebar.radio(
    "Gender",
    ["All"] + gender_options
)


marital_options = (
    sorted(df["Marital_Status"].dropna().unique())
    if "Marital_Status" in df.columns
    else []
)

selected_marital = []

for status in marital_options:
    if st.sidebar.checkbox(status, value=True):
        selected_marital.append(status)


if st.sidebar.button("🔄 Reset Filters"):
    st.rerun()


# ---------------- FILTER DATA ----------------

filtered = df.copy()

if selected_zones:
    filtered = filtered[
        filtered["Zone"].isin(selected_zones)
    ]

if selected_states:
    filtered = filtered[
        filtered["State"].isin(selected_states)
    ]

if selected_ages:
    filtered = filtered[
        filtered["Age_Group"].isin(selected_ages)
    ]

if selected_gender != "All":
    filtered = filtered[
        filtered["Gender"] == selected_gender
    ]

if selected_marital:
    filtered = filtered[
        filtered["Marital_Status"].isin(selected_marital)
    ]


# ---------------- THEME ----------------

template = "plotly_dark" if dark_mode else "plotly_white"

if dark_mode:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117;
        }

        .kpi {
            padding: 20px;
            border-radius: 12px;
            background: #161b22;
            border: 1px solid #30363d;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .kpi {
            padding: 20px;
            border-radius: 12px;
            background: white;
            border: 1px solid #e5e7eb;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ---------------- HEADER ----------------

st.title("📊 Sales Data Analysis Dashboard")
st.caption("Interactive Retail Sales Dashboard")


# ---------------- KPI ----------------

revenue = (
    filtered["Amount"].sum()
    if "Amount" in filtered.columns
    else 0
)

orders = (
    filtered["Orders"].sum()
    if "Orders" in filtered.columns
    else 0
)

customers = (
    filtered["User_ID"].nunique()
    if "User_ID" in filtered.columns
    else 0
)

aov = revenue / orders if orders else 0


c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("💰 Total Revenue", f"₹{revenue:,.2f}")

with c2:
    st.metric("📦 Total Orders", f"{int(orders):,}")

with c3:
    st.metric("👥 Unique Customers", f"{customers:,}")

with c4:
    st.metric("🧾 Average Order Value", f"₹{aov:,.2f}")


st.divider()


# ---------------- AGE / GENDER ----------------

st.subheader("👥 Age Group & Gender Analysis")

left, right = st.columns(2)

if not filtered.empty and "Age_Group" in filtered.columns:

    age_gender = (
        filtered
        .groupby(["Age_Group", "Gender"], as_index=False)
        .agg(
            Orders=("Orders", "sum"),
            Amount=("Amount", "sum")
        )
    )

    gender_colors = {
        "M": "#1565C0",
        "F": "#90CAF9"
    }

    fig1 = px.bar(
        age_gender,
        x="Age_Group",
        y="Orders",
        color="Gender",
        barmode="group",
        category_orders={"Age_Group": age_order},
        color_discrete_map=gender_colors,
        title="Orders by Age Group & Gender",
        template=template
    )

    left.plotly_chart(
        fig1,
        use_container_width=True
    )


    fig2 = px.bar(
        age_gender,
        x="Age_Group",
        y="Amount",
        color="Gender",
        barmode="group",
        category_orders={"Age_Group": age_order},
        color_discrete_map=gender_colors,
        title="Amount by Age Group & Gender",
        template=template
    )

    right.plotly_chart(
        fig2,
        use_container_width=True
    )


st.divider()


# ---------------- DONUT CHARTS ----------------

st.subheader("📍 Zone & Marital Status")

left, right = st.columns(2)


if "Zone" in filtered.columns:

    zone_data = (
        filtered
        .groupby("Zone", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )

    fig3 = px.pie(
        zone_data,
        names="Zone",
        values="Amount",
        hole=0.45,
        title="Zone-wise Revenue",
        template=template
    )

    left.plotly_chart(
        fig3,
        use_container_width=True
    )


if "Marital_Status" in filtered.columns:

    marital_data = (
        filtered
        .groupby("Marital_Status", as_index=False)["Amount"]
        .sum()
    )

    fig4 = px.pie(
        marital_data,
        names="Marital_Status",
        values="Amount",
        hole=0.45,
        title="Marital Status Revenue",
        template=template
    )

    right.plotly_chart(
        fig4,
        use_container_width=True
    )


st.divider()


# ---------------- SECTOR ----------------

st.subheader("🏢 Sector Performance")

left, right = st.columns(2)

if "Sector" in filtered.columns:

    sector_data = (
        filtered
        .groupby("Sector")
        .agg(
            Total_Orders=("Orders", "sum"),
            Average_Orders=("Orders", "mean")
        )
        .reset_index()
        .sort_values("Total_Orders", ascending=False)
    )

    fig5 = px.bar(
        sector_data,
        x="Sector",
        y="Total_Orders",
        title="Sector-wise Total Orders",
        template=template
    )

    fig5.update_layout(
        xaxis_tickangle=-45
    )

    left.plotly_chart(
        fig5,
        use_container_width=True
    )


    fig6 = px.bar(
        sector_data,
        x="Sector",
        y="Average_Orders",
        title="Sector-wise Average Orders",
        template=template
    )

    fig6.update_layout(
        xaxis_tickangle=-45
    )

    right.plotly_chart(
        fig6,
        use_container_width=True
    )


st.divider()


# ---------------- STATES & PRODUCTS ----------------

st.subheader("🏆 Top States & Product Categories")

left, right = st.columns(2)


if "State" in filtered.columns:

    top_states = (
        filtered
        .groupby("State", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
        .head(10)
    )

    fig7 = px.bar(
        top_states,
        x="Amount",
        y="State",
        orientation="h",
        title="Top 10 States by Revenue",
        template=template
    )

    left.plotly_chart(
        fig7,
        use_container_width=True
    )


if "Product_Category" in filtered.columns:

    product_data = (
        filtered
        .groupby("Product_Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
        .head(10)
    )

    fig8 = px.bar(
        product_data,
        x="Amount",
        y="Product_Category",
        orientation="h",
        title="Top Product Categories by Revenue",
        template=template
    )

    right.plotly_chart(
        fig8,
        use_container_width=True
    )


st.divider()


# ---------------- RAW DATA ----------------

st.subheader("📋 Filtered Data")

with st.expander("Show Raw Data"):

    st.dataframe(
        filtered,
        use_container_width=True
    )

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Filtered CSV",
        csv,
        "sales_filtered.csv",
        "text/csv"
    )


st.caption(
    "Sales Data Analysis Dashboard • Built with Streamlit, Pandas & Plotly"
)