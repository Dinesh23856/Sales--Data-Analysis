# 📊 Sales Data Science Project

📌 Project Overview

This project performs Exploratory Data Analysis (EDA) on retail sales data to understand sales performance and customer behavior across different:

- 👥 Age groups and gender
- 🏢 Sectors
- 🌍 Zones
- 📍 States
- 🛍️ Product categories
- 💍 Marital status

The project uses Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter Notebook, Streamlit, and Plotly to clean, analyze, visualize, and present sales data.

The project also includes an interactive Streamlit Sales Data Analysis Dashboard for exploring important sales and customer metrics.

---

🎯 Objectives

The main objectives of this project are:

- 📦 Analyze overall order performance
- 💰 Analyze overall sales/revenue performance
- 👥 Analyze age group-wise gender distribution
- 🏢 Analyze sector-wise total orders
- 📈 Analyze sector-wise average orders
- 💵 Analyze sector-wise total amount
- 🌍 Analyze zone-wise total amount
- 🏆 Identify the top states by sales amount
- 🛍️ Analyze product-category-wise average orders
- 📦 Analyze product-category-wise total orders
- 🏅 Analyze top product categories by sales amount
- 💍 Analyze marital-status-wise total amount
- 📊 Build an interactive sales dashboard

---

📂 Dataset

The project uses a retail sales dataset stored in an Excel file:

project Data new.xlsx

The dataset contains customer, geographical, sector, product, order, and sales information.

Dataset Columns

The original dataset contains the following columns:

Column| Description
"User_ID"| Unique customer/user identifier
"Cust_name"| Customer name
"Product_ID"| Product identifier
"Gender"| Customer gender
"Age Group"| Customer age group
"Age"| Customer age
"Marital_Status"| Customer marital status
"State"| Customer state
"Zone"| Geographic zone
"Occupation"| Customer occupation/sector
"Product_Category"| Product category
"Orders"| Number of orders
"Amount"| Sales amount
"Status"| Status field
"unnamed1"| Unused/empty field

---

📊 Dataset Information

The original dataset contains:

- 📌 Rows: 11,251
- 📌 Columns: 15
- 📌 Amount missing values: 12
- 📌 Status missing values: 11,251
- 📌 unnamed1 missing values: 11,251

The notebook uses "df.info()" and "df.isnull().sum()" to inspect the dataset structure and missing values.

After cleaning, the unused "Status" and "unnamed1" columns are removed.

---

🧹 Data Cleaning

The following data-cleaning operations are performed:

1. Rename Occupation

The original "Occupation" column is renamed to "Sector" to make the analysis terminology more suitable for the project.

df.rename(columns={"Occupation": "Sector"}, inplace=True)

2. Convert Marital Status

The original marital-status values are converted:

0 → Single
1 → Married

3. Remove Unnecessary Columns

The following columns are removed:

Status
unnamed1

4. Missing Value Analysis

Missing values are checked using:

df.isnull().sum()

5. Age Group Analysis

Unique age groups are checked before performing the age-group analysis.

The dataset contains these age groups:

0-17
18-25
26-35
36-45
46-50
51-55
55+

---

🔎 Exploratory Data Analysis

The project performs exploratory analysis to understand relationships between sales, orders, customers, geography, sectors, and products.

👥 Age Group & Gender Analysis

The project analyzes order and sales distribution across different age groups and genders.

Age groups analyzed include:

- 0-17
- 18-25
- 26-35
- 36-45
- 46-50
- 51-55
- 55+

---

🏢 Sector Analysis

Sector-level performance is analyzed using:

- Total orders
- Average orders
- Total sales amount

The dataset contains sectors such as:

- IT Sector
- Healthcare
- Aviation
- Banking
- Govt
- Hospitality
- Media
- Automobile
- Lawyer
- Chemical
- Retail
- Food Processing
- Construction
- Textile
- Agriculture

---

🌍 Zone Analysis

Sales amount is analyzed across different zones:

- Central
- Southern
- Western
- Northern
- Eastern

---

📍 State Analysis

States are grouped according to total sales amount to identify high-performing states.

---

🛍️ Product Category Analysis

Product categories are analyzed using:

- Average orders
- Total orders
- Total sales amount

Examples of product categories include:

- Food
- Clothing & Apparel
- Electronics & Gadgets
- Footwear & Shoes
- Furniture
- Games & Toys
- Sports Products
- Beauty
- Auto
- Stationery
- Household items
- Pet Care
- Veterinary

---

💍 Marital Status Analysis

Sales amount is analyzed based on customer marital status:

- Single
- Married

---

📈 Analysis & Visualizations

The project contains the following major analyses and visualizations:

1. 👥 Age Group-wise Gender Analysis

Visualizes orders and sales amount across age groups and gender.

2. 📈 Sector-wise Average Orders

Calculates and visualizes the average number of orders for each sector.

3. 📦 Sector-wise Total Orders

Groups the dataset by sector and calculates total orders.

4. 🌍 Zone-wise Total Amount

Calculates the total sales amount contributed by each zone.

5. 🏆 Top 10 States by Amount

Groups states by total sales amount and identifies the top-performing states.

6. 💰 Sector-wise Total Amount

Analyzes total sales amount generated by each sector.

7. 📈 Product Category-wise Average Orders

Calculates the average number of orders for each product category.

8. 📦 Product Category-wise Total Orders

Calculates total orders for each product category.

9. 💍 Marital Status-wise Total Amount

Analyzes total sales amount for Single and Married customers.

10. 🏅 Top Product Categories by Amount

Identifies product categories generating the highest sales amount.

---

📊 Interactive Dashboard

The project includes an interactive Sales Data Analysis Dashboard built using Streamlit, Pandas, and Plotly.

The dashboard provides a visual summary of the sales data.

Dashboard Features

💰 Key Metrics

The dashboard displays:

- Total Revenue
- Total Orders
- Unique Customers
- Average Order Value

The dashboard output shows 28,007 total orders and 3,755 unique customers.

👥 Age Group & Gender

The dashboard provides:

- Total Orders by Age Group & Gender
- Total Revenue by Age Group & Gender

🌍 Zone & Marital Status

The dashboard includes:

- Zone-wise Revenue Contribution
- Marital Status Revenue Contribution

The displayed dashboard shows:

Category| Contribution
Central Zone| 39.2%
Southern Zone| 25.0%
Western Zone| 17.3%
Northern Zone| 11.9%
Eastern Zone| 6.63%
Single| 58.5%
Married| 41.5%

These values are shown in the dashboard's zone and marital-status charts.

🏢 Sector Performance

The dashboard provides:

- Sector-wise Total Orders
- Sector-wise Average Orders per Record
- Sector-wise Total Revenue

🏆 Top States & Product Categories

The dashboard provides:

- Top 10 States by Revenue
- Top 10 Product Categories by Revenue

The displayed product-category chart includes categories such as Food, Clothing & Apparel, Electronics & Gadgets, Footwear & Shoes, Furniture, Games & Toys, Sports Products, Beauty, Auto, and Stationery.

🛍️ Product Category Orders

The dashboard provides:

- Top 10 Categories by Total Orders
- Top 10 Categories by Average Orders

📋 Filtered Data

The dashboard also provides a section for viewing filtered/raw sales data.

---

🛠️ Technologies Used

Programming & Data Analysis

- 🐍 Python
- 🐼 Pandas
- 🔢 NumPy

Data Visualization

- 📊 Matplotlib
- 📈 Seaborn
- 📉 Plotly

Dashboard

- 🎨 Streamlit

Development Environment

- 📓 Jupyter Notebook
- 💻 VS Code / JupyterLab

Data & File Handling

- 📗 Microsoft Excel
- 📄 CSV
- 📦 OpenPyXL

---

📁 Project Structure

Sales--Data-Analysis/
│
├── 📓 Sales_Analysis.ipynb
├── 📓 Sales_EDA.ipynb
│
├── 📊 app.py
│
├── 📄 project Data new.xlsx
│
├── 📄 Product_Category_Table.csv
├── 📄 Sector_Table.csv
├── 📄 State_Table.csv
├── 📄 Zone_Table.csv
│
├── 📄 requirements.txt
├── 📖 README.md
└── ⚖️ LICENSE

«Update the filenames above if your actual GitHub repository uses different names.»

---

⚙️ Installation

1. Clone the Repository

git clone https://github.com/your-username/Sales--Data-Analysis.git

Move into the project directory:

cd Sales--Data-Analysis

2. Install Required Libraries

If "requirements.txt" is available:

pip install -r requirements.txt

Alternatively, install the main libraries manually:

pip install pandas numpy matplotlib seaborn plotly streamlit openpyxl jupyter

---

▶️ How to Run

📓 Run the Jupyter Notebook

Open:

Sales_Analysis.ipynb

using Jupyter Notebook, JupyterLab, or VS Code.

Run the cells sequentially to reproduce the data cleaning, analysis, and visualizations.

📊 Run the Streamlit Dashboard

If your Streamlit application is named "app.py", run:

streamlit run app.py

The dashboard will open in your web browser.

---

📂 Dataset Path

The notebook should load the dataset using a relative path so that it works correctly on GitHub and on other computers:

df = pd.read_excel("project Data new.xlsx")

Make sure:

project Data new.xlsx

is located in the repository root.

If the Excel file is stored in another folder, update the path accordingly.

---

💡 Key Insights

The analysis provides insights into:

- 🏢 Sector-wise order performance
- 💰 Sector-wise revenue performance
- 🌍 Revenue contribution by zone
- 📍 State-wise sales performance
- 🛍️ Product category performance
- 📦 Product category order volume
- 👥 Customer distribution by age group and gender
- 💍 Revenue contribution by marital status

Dashboard Findings

Based on the displayed dashboard:

- 🥇 Central has the largest zone-wise revenue contribution at 39.2%.
- 🥈 Southern contributes 25.0%.
- Western contributes 17.3%.
- Northern contributes 11.9%.
- Eastern contributes 6.63%.
- 👤 Single customers contribute 58.5% of marital-status revenue.
- 💍 Married customers contribute 41.5%.
- 📦 The dashboard reports 28,007 total orders.
- 👥 The dashboard reports 3,755 unique customers.

---

📸 Dashboard Preview

Sales Data Analysis Dashboard

The dashboard provides an interactive view of:

- Total Revenue
- Total Orders
- Unique Customers
- Average Order Value
- Age Group & Gender Analysis
- Zone-wise Revenue
- Marital Status Revenue
- Sector Performance
- Top States
- Top Product Categories
- Product Category Orders
- Sector-wise Revenue
- Filtered/Raw Data

The dashboard is built with Streamlit, Pandas, and Plotly.

---

📌 Project Workflow

Excel Dataset
      ↓
Data Loading
      ↓
Data Inspection
      ↓
Missing Value Analysis
      ↓
Data Cleaning
      ↓
Feature/Column Preparation
      ↓
Exploratory Data Analysis
      ↓
Data Visualization
      ↓
Sales Insights
      ↓
Interactive Streamlit Dashboard

---

📚 Main Analysis Categories

Analysis| Metric
Age Group & Gender| Orders & Amount
Sector| Total Orders
Sector| Average Orders
Sector| Total Amount
Zone| Total Amount
State| Top 10 by Amount
Product Category| Average Orders
Product Category| Total Orders
Product Category| Top Categories by Amount
Marital Status| Total Amount

---

🎓 Skills Demonstrated

This project demonstrates practical skills in:

- 🐍 Python programming
- 🐼 Data manipulation using Pandas
- 🔢 NumPy
- 🧹 Data cleaning
- 🔍 Exploratory Data Analysis
- 📊 Data visualization
- 📈 GroupBy and aggregation
- 📉 Statistical summaries
- 🛍️ Business-oriented sales analysis
- 🎨 Dashboard development
- 🎯 Data storytelling
- 📊 Streamlit application development

---

👨‍💻 Author

Dinesh More

📊 Data Science Project

---

📜 License

This project is licensed under the MIT License.

