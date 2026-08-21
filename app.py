import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Sales Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. DATA LOADING & CLEANING PIPELINE
# ==========================================
@st.cache_data
def load_data():
    try:
        base_dir = Path(__file__).resolve().parent
    except NameError:
        base_dir = Path.cwd()
        
    file_path = base_dir / "project Data new.xlsx"
    
    if not file_path.exists():
        file_path = Path("project Data new.xlsx")
        
    if not file_path.exists():
        st.error(f"Dataset file not found at: {file_path.resolve()}. Please ensure 'project Data new.xlsx' is in the app directory.")
        st.stop()

    df = pd.read_excel(file_path, engine="openpyxl")
    
    # Clean column headers
    df.columns = df.columns.astype(str).str.strip()
    
    # Drop unnecessary columns if they exist
    cols_to_drop = [c for c in ["unnamed1", "Status", "Unnamed: 0"] if c in df.columns]
    if cols_to_drop:
        df.drop(columns=cols_to_drop, inplace=True)
        
    # Standardize column names
    rename_dict = {
        "Occupation": "Sector",
        "Age Group": "Age_Group",
        "Product Category": "Product_Category"
    }
    df.rename(columns={k: v for k, v in rename_dict.items() if k in df.columns}, inplace=True)
    
    # Required columns validation
    required_cols = [
        "User_ID", "Gender", "Age_Group", "Marital_Status", 
        "State", "Zone", "Sector", "Product_Category", "Orders", "Amount"
    ]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns in dataset: {missing_cols}")
        st.stop()
        
    # Strip string columns
    string_cols = ["Gender", "Age_Group", "State", "Zone", "Sector", "Product_Category"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Normalize Gender
    gender_map = {"M": "M", "Male": "M", "F": "F", "Female": "F"}
    df["Gender"] = df["Gender"].map(lambda x: gender_map.get(x, x))
    
    # Normalize Marital_Status
    def clean_marital_status(val):
        s = str(val).strip().lower()
        if s in ["1", "1.0", "married"]:
            return "Married"
        elif s in ["0", "0.0", "single"]:
            return "Single"
        return str(val).strip()
        
    df["Marital_Status"] = df["Marital_Status"].apply(clean_marital_status)
    
    # Clean numeric fields
    df["Orders"] = pd.to_numeric(df["Orders"], errors="coerce").fillna(0).astype(int)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    
    # Filter out rows with zero or null User_ID if any
    df = df[df["User_ID"].notnull()].copy()
    
    return df

df_raw = load_data()

# ==========================================
# 3. SIDEBAR FILTERS & THEME
# ==========================================
st.sidebar.title("Dashboard Filters")

# Theme selection
dark_mode = st.sidebar.toggle("Dark Mode", value=True)
plotly_template = "plotly_dark" if dark_mode else "plotly_white"
bg_card_color = "#1E1E1E" if dark_mode else "#F8F9FA"
text_color = "#FFFFFF" if dark_mode else "#111111"

# Reset filter handler
if "filter_version" not in st.session_state:
    st.session_state["filter_version"] = 0

if st.sidebar.button("Reset Filters", use_container_width=True):
    st.session_state["filter_version"] += 1
    st.rerun()

v_key = st.session_state["filter_version"]

# 1. Zone filter
all_zones = sorted(df_raw["Zone"].dropna().unique().tolist())
selected_zones = st.sidebar.multiselect(
    "Select Zone:",
    options=all_zones,
    default=all_zones,
    key=f"zone_{v_key}"
)

# 2. Dynamic State filter based on Zone
available_states = sorted(df_raw[df_raw["Zone"].isin(selected_zones)]["State"].dropna().unique().tolist()) if selected_zones else []
selected_states = st.sidebar.multiselect(
    "Select State:",
    options=available_states,
    default=available_states,
    key=f"state_{v_key}"
)

# 3. Age Group filter
age_order = ["0-17", "18-25", "26-35", "36-45", "46-50", "51-55", "55+"]
raw_age_groups = [ag for ag in age_order if ag in df_raw["Age_Group"].unique()]
other_age_groups = [ag for ag in df_raw["Age_Group"].unique() if ag not in age_order]
all_age_groups = raw_age_groups + sorted(other_age_groups)

selected_age_groups = st.sidebar.multiselect(
    "Select Age Group:",
    options=all_age_groups,
    default=all_age_groups,
    key=f"age_{v_key}"
)

# 4. Gender filter
gender_options = ["All"] + sorted([g for g in df_raw["Gender"].dropna().unique().tolist() if g in ["M", "F"]])
selected_gender = st.sidebar.selectbox(
    "Select Gender:",
    options=gender_options,
    index=0,
    key=f"gender_{v_key}"
)

# 5. Marital Status filter
all_marital_statuses = sorted(df_raw["Marital_Status"].dropna().unique().tolist())
selected_marital_status = st.sidebar.multiselect(
    "Select Marital Status:",
    options=all_marital_statuses,
    default=all_marital_statuses,
    key=f"marital_{v_key}"
)

# ==========================================
# 4. FILTERING LOGIC
# ==========================================
if not selected_zones or not selected_states or not selected_age_groups or not selected_marital_status:
    filtered_df = pd.DataFrame(columns=df_raw.columns)
else:
    mask = (
        df_raw["Zone"].isin(selected_zones) &
        df_raw["State"].isin(selected_states) &
        df_raw["Age_Group"].isin(selected_age_groups) &
        df_raw["Marital_Status"].isin(selected_marital_status)
    )
    if selected_gender != "All":
        mask = mask & (df_raw["Gender"] == selected_gender)
        
    filtered_df = df_raw[mask].copy()

# ==========================================
# 5. DASHBOARD HEADER
# ==========================================
st.title("Sales Data Analysis Dashboard")
st.caption("Interactive Retail Sales Performance & Customer Demographics Overview")
st.markdown("---")

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filter combination. Please select at least one valid option for Zone, State, Age Group, and Marital Status.")
    st.stop()

# ==========================================
# 6. KPI CARDS
# ==========================================
total_revenue = filtered_df["Amount"].sum()
total_orders = filtered_df["Orders"].sum()
unique_customers = filtered_df["User_ID"].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Total Revenue", value=f"₹{total_revenue:,.2f}")

with kpi2:
    st.metric(label="Total Orders", value=f"{total_orders:,}")

with kpi3:
    st.metric(label="Unique Customers", value=f"{unique_customers:,}")

with kpi4:
    st.metric(label="Average Order Value (AOV)", value=f"₹{avg_order_value:,.2f}")

st.markdown("---")

# ==========================================
# 7. SECTION 1: AGE GROUP & GENDER ANALYSIS
# ==========================================
st.subheader("Age Group & Gender Analysis")
col1, col2 = st.columns(2)

gender_color_map = {"M": "#1565C0", "F": "#90CAF9"}

# Chart 1: Total Orders by Age Group & Gender
agg_age_orders = filtered_df.groupby(["Age_Group", "Gender"], as_index=False)["Orders"].sum()
agg_age_orders["Age_Group"] = pd.Categorical(agg_age_orders["Age_Group"], categories=all_age_groups, ordered=True)
agg_age_orders = agg_age_orders.sort_values(["Age_Group", "Gender"])

fig_age_orders = px.bar(
    agg_age_orders,
    x="Age_Group",
    y="Orders",
    color="Gender",
    barmode="group",
    title="Total Orders by Age Group & Gender",
    labels={"Age_Group": "Age Group", "Orders": "Total Orders", "Gender": "Gender"},
    color_discrete_map=gender_color_map,
    template=plotly_template
)
fig_age_orders.update_layout(xaxis_title="Age Group", yaxis_title="Total Orders", legend_title="Gender")

with col1:
    st.plotly_chart(fig_age_orders, use_container_width=True)

# Chart 2: Total Revenue by Age Group & Gender
agg_age_rev = filtered_df.groupby(["Age_Group", "Gender"], as_index=False)["Amount"].sum()
agg_age_rev["Age_Group"] = pd.Categorical(agg_age_rev["Age_Group"], categories=all_age_groups, ordered=True)
agg_age_rev = agg_age_rev.sort_values(["Age_Group", "Gender"])

fig_age_rev = px.bar(
    agg_age_rev,
    x="Age_Group",
    y="Amount",
    color="Gender",
    barmode="group",
    title="Total Revenue by Age Group & Gender",
    labels={"Age_Group": "Age Group", "Amount": "Total Revenue (₹)", "Gender": "Gender"},
    color_discrete_map=gender_color_map,
    template=plotly_template
)
fig_age_rev.update_layout(xaxis_title="Age Group", yaxis_title="Total Revenue (₹)", legend_title="Gender")

with col2:
    st.plotly_chart(fig_age_rev, use_container_width=True)

st.markdown("---")

# ==========================================
# 8. SECTION 2: ZONE & MARITAL STATUS
# ==========================================
st.subheader("Zone & Marital Status Contribution")
col3, col4 = st.columns(2)

# Chart 3: Zone-wise Revenue Contribution (Donut)
zone_rev = filtered_df.groupby("Zone", as_index=False)["Amount"].sum()
fig_zone_donut = px.pie(
    zone_rev,
    names="Zone",
    values="Amount",
    hole=0.55,
    title="Zone-wise Revenue Contribution",
    template=plotly_template,
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig_zone_donut.update_traces(textposition="inside", textinfo="percent+label")
fig_zone_donut.update_layout(legend_title="Zone")

with col3:
    st.plotly_chart(fig_zone_donut, use_container_width=True)

# Chart 4: Marital Status Revenue Contribution (Donut)
marital_rev = filtered_df.groupby("Marital_Status", as_index=False)["Amount"].sum()
marital_color_map = {"Married": "#5C6BC0", "Single": "#26A69A"}
fig_marital_donut = px.pie(
    marital_rev,
    names="Marital_Status",
    values="Amount",
    hole=0.55,
    title="Marital Status Revenue Contribution",
    template=plotly_template,
    color="Marital_Status",
    color_discrete_map=marital_color_map
)
fig_marital_donut.update_traces(textposition="inside", textinfo="percent+label")
fig_marital_donut.update_layout(legend_title="Marital Status")

with col4:
    st.plotly_chart(fig_marital_donut, use_container_width=True)

st.markdown("---")

# ==========================================
# 9. SECTION 3: SECTOR PERFORMANCE
# ==========================================
st.subheader("Sector Performance")
col5, col6 = st.columns(2)

# Chart 5: Sector-wise Total Orders (Horizontal Bar)
sector_orders = filtered_df.groupby("Sector", as_index=False)["Orders"].sum().sort_values(by="Orders", ascending=True)

fig_sector_orders = px.bar(
    sector_orders,
    x="Orders",
    y="Sector",
    orientation="h",
    title="Sector-wise Total Orders",
    labels={"Orders": "Total Orders", "Sector": "Sector"},
    template=plotly_template,
    color_discrete_sequence=["#5C6BC0"]
)
fig_sector_orders.update_layout(xaxis_title="Total Orders", yaxis_title="Sector")

with col5:
    st.plotly_chart(fig_sector_orders, use_container_width=True)

# Chart 6: Sector-wise Average Orders per Record (Horizontal Bar)
sector_avg_orders = filtered_df.groupby("Sector", as_index=False)["Orders"].mean().rename(columns={"Orders": "Average_Orders"}).sort_values(by="Average_Orders", ascending=True)

fig_sector_avg = px.bar(
    sector_avg_orders,
    x="Average_Orders",
    y="Sector",
    orientation="h",
    title="Sector-wise Average Orders per Record",
    labels={"Average_Orders": "Average Orders per Record", "Sector": "Sector"},
    template=plotly_template,
    color_discrete_sequence=["#7E57C2"]
)
fig_sector_avg.update_layout(xaxis_title="Average Orders per Record", yaxis_title="Sector")

with col6:
    st.plotly_chart(fig_sector_avg, use_container_width=True)

st.markdown("---")

# ==========================================
# 10. SECTION 4: TOP STATES & PRODUCT CATEGORIES BY REVENUE
# ==========================================
st.subheader("Top States & Product Categories by Revenue")
col7, col8 = st.columns(2)

# Chart 7: Top 10 States by Revenue (Horizontal Bar)
top_states_rev = filtered_df.groupby("State", as_index=False)["Amount"].sum().sort_values(by="Amount", ascending=False).head(10)
top_states_rev = top_states_rev.sort_values(by="Amount", ascending=True)

fig_top_states = px.bar(
    top_states_rev,
    x="Amount",
    y="State",
    orientation="h",
    title="Top 10 States by Revenue",
    labels={"Amount": "Revenue (₹)", "State": "State"},
    template=plotly_template,
    color_discrete_sequence=["#42A5F5"]
)
fig_top_states.update_layout(xaxis_title="Revenue (₹)", yaxis_title="State")

with col7:
    st.plotly_chart(fig_top_states, use_container_width=True)

# Chart 8: Top 10 Product Categories by Revenue (Horizontal Bar)
top_cat_rev = filtered_df.groupby("Product_Category", as_index=False)["Amount"].sum().sort_values(by="Amount", ascending=False).head(10)
top_cat_rev = top_cat_rev.sort_values(by="Amount", ascending=True)

fig_top_cat_rev = px.bar(
    top_cat_rev,
    x="Amount",
    y="Product_Category",
    orientation="h",
    title="Top 10 Product Categories by Revenue",
    labels={"Amount": "Revenue (₹)", "Product_Category": "Product Category"},
    template=plotly_template,
    color_discrete_sequence=["#26A69A"]
)
fig_top_cat_rev.update_layout(xaxis_title="Revenue (₹)", yaxis_title="Product Category")

with col8:
    st.plotly_chart(fig_top_cat_rev, use_container_width=True)

st.markdown("---")

# ==========================================
# 11. SECTION 5: PRODUCT CATEGORY ORDERS
# ==========================================
st.subheader("Product Category Orders Breakdown")
col9, col10 = st.columns(2)

# Chart 9: Top 10 Categories by Total Orders (Horizontal Bar)
top_cat_orders = filtered_df.groupby("Product_Category", as_index=False)["Orders"].sum().sort_values(by="Orders", ascending=False).head(10)
top_cat_orders = top_cat_orders.sort_values(by="Orders", ascending=True)

fig_top_cat_orders = px.bar(
    top_cat_orders,
    x="Orders",
    y="Product_Category",
    orientation="h",
    title="Top 10 Categories by Total Orders",
    labels={"Orders": "Total Orders", "Product_Category": "Product Category"},
    template=plotly_template,
    color_discrete_sequence=["#66BB6A"]
)
fig_top_cat_orders.update_layout(xaxis_title="Total Orders", yaxis_title="Product Category")

with col9:
    st.plotly_chart(fig_top_cat_orders, use_container_width=True)

# Chart 10: Top 10 Categories by Average Orders per Record (Horizontal Bar)
top_cat_avg_orders = filtered_df.groupby("Product_Category", as_index=False)["Orders"].mean().rename(columns={"Orders": "Average_Orders"}).sort_values(by="Average_Orders", ascending=False).head(10)
top_cat_avg_orders = top_cat_avg_orders.sort_values(by="Average_Orders", ascending=True)

fig_top_cat_avg = px.bar(
    top_cat_avg_orders,
    x="Average_Orders",
    y="Product_Category",
    orientation="h",
    title="Top 10 Categories by Average Orders per Record",
    labels={"Average_Orders": "Average Orders per Record", "Product_Category": "Product Category"},
    template=plotly_template,
    color_discrete_sequence=["#FFA726"]
)
fig_top_cat_avg.update_layout(xaxis_title="Average Orders per Record", yaxis_title="Product Category")

with col10:
    st.plotly_chart(fig_top_cat_avg, use_container_width=True)

st.markdown("---")

# ==========================================
# 12. SECTION 6: SECTOR-WISE TOTAL REVENUE
# ==========================================
st.subheader("Sector-wise Total Revenue")

sector_rev = filtered_df.groupby("Sector", as_index=False)["Amount"].sum().sort_values(by="Amount", ascending=True)

fig_sector_rev = px.bar(
    sector_rev,
    x="Amount",
    y="Sector",
    orientation="h",
    title="Sector-wise Total Revenue",
    labels={"Amount": "Total Revenue (₹)", "Sector": "Sector"},
    template=plotly_template,
    color_discrete_sequence=["#EC407A"]
)
fig_sector_rev.update_layout(xaxis_title="Total Revenue (₹)", yaxis_title="Sector")

st.plotly_chart(fig_sector_rev, use_container_width=True)

st.markdown("---")

# ==========================================
# 13. SECTION 7: FILTERED RAW DATA & CSV DOWNLOAD
# ==========================================
st.subheader("Filtered Raw Data")

with st.expander("Show Raw Data Table", expanded=False):
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)

@st.cache_data
def convert_df_to_csv(df_to_convert):
    return df_to_convert.to_csv(index=False).encode("utf-8")

csv_data = convert_df_to_csv(filtered_df)

st.download_button(
    label="📥 Download Filtered CSV",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
    use_container_width=False
)

# ==========================================
# 14. FOOTER
# ==========================================
st.markdown("<br><hr><center style='color: gray;'>Sales Data Analysis Dashboard | Built with Streamlit, Pandas & Plotly</center>", unsafe_allow_html=True)
