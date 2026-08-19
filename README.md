📊 Sales Analysis Project

📌 Project Overview

This project performs Exploratory Data Analysis (EDA) on retail sales data to understand sales performance across different sectors, zones, states, product categories, age groups, gender, and marital status.

The analysis uses Python, Pandas, NumPy, Matplotlib, and Seaborn to clean, analyze, and visualize the sales data.

---

🎯 Objectives

- 📦 Analyze overall sales and order performance
- 🏢 Analyze sector-wise total orders
- 📈 Analyze sector-wise average orders
- 💰 Analyze sector-wise total amount
- 🌍 Analyze zone-wise total amount
- 🏆 Identify the top 10 states by sales amount
- 🛍️ Analyze product-category-wise average and total orders
- 💵 Analyze marital-status-wise total amount
- 🏅 Identify the top 10 product categories by amount
- 👥 Analyze age group-wise gender distribution

---

🛠️ Technologies Used

- 🐍 Python
- 🐼 Pandas
- 🔢 NumPy
- 📊 Matplotlib
- 📈 Seaborn
- 📓 Jupyter Notebook
- 📗 Excel
- 📄 CSV
- 📦 OpenPyXL

---

📂 Dataset

The project uses a retail sales dataset stored in an Excel file.

The analysis uses fields such as:

- 📍 State
- 🌎 Zone
- 🏢 Sector
- 🛍️ Product Category
- 📦 Orders
- 💰 Amount
- 🎂 Age Group
- 👤 Gender
- 💍 Marital Status

⚠️ Dataset Requirement

The notebook currently loads the Excel dataset using a local Windows file path:

"project Data new.xlsx"

Make sure the dataset is available and update the file path in the notebook before running it.

---

🧹 Data Cleaning

The following data-cleaning steps were performed:

- ✏️ Renamed "Occupation" to "Sector"
- 💍 Converted "Marital_Status" value "1" to "Married"
- 💍 Converted "Marital_Status" value "0" to "Single"
- 🗑️ Removed unnecessary columns: "unnamed1" and "Status"
- 🔍 Checked missing values
- 🔎 Checked unique age groups
- 📋 Created a separate State DataFrame from unique states

---

📊 Analysis & Visualizations

The project includes the following analyses:

1. 👥 Age Group-wise Gender Analysis
2. 📈 Sector-wise Average Orders
3. 📦 Sector-wise Total Orders
4. 🌍 Zone-wise Total Amount
5. 🏆 Top 10 States by Amount
6. 💰 Sector-wise Total Amount
7. 📈 Product Category-wise Average Orders
8. 📦 Product Category-wise Total Orders
9. 💍 Marital Status-wise Total Amount
10. 🏅 Top 10 Product Categories by Amount

---

📁 Project Files

File| Description
"Sales_Analysis.ipynb"| 📊 Main sales analysis notebook
"Sales_EDA.ipynb"| 🔎 Exploratory data analysis notebook
"Product_Category_Table.csv"| 🛍️ Product category reference table
"Sector_Table.csv"| 🏢 Sector reference table
"State_Table.csv"| 📍 State reference table
"Zone_Table.csv"| 🌍 Zone reference table
"README.md"| 📖 Project documentation
"LICENSE"| ⚖️ Project license

---

📂 Project Structure

Sales--Data-Analysis/
│
├── 📓 Sales_Analysis.ipynb
├── 📓 Sales_EDA.ipynb
├── 📄 Product_Category_Table.csv
├── 📄 Sector_Table.csv
├── 📄 State_Table.csv
├── 📄 Zone_Table.csv
├── 📖 README.md
├── ⚖️ LICENSE
└── 📄 project Data new.xlsx

«⚠️ If "project Data new.xlsx" is not uploaded to the repository, remove it from the structure above and keep the dataset requirement note instead.»

---

▶️ How to Run

1️⃣ Clone or download the repository

Download the project from GitHub.

2️⃣ Install the required libraries

pip install pandas numpy matplotlib seaborn openpyxl jupyter

3️⃣ Open the notebook

Open:

Sales_Analysis.ipynb

using Jupyter Notebook, JupyterLab, or another compatible notebook environment.

4️⃣ Set the dataset path

Update the Excel file path in the notebook:

df = pd.read_excel("project Data new.xlsx")

5️⃣ Run the notebook

Run the cells sequentially to reproduce the analysis and visualizations.

---

💡 Key Insights

The analysis helps identify:

- 🏢 Which sectors generate the highest number of orders
- 💰 Which sectors generate the highest sales amount
- 🌍 Which zones contribute the most to total sales
- 🏆 Which states have the highest sales amount
- 🛍️ Which product categories have the highest orders
- 💵 Sales distribution across marital status
- 👥 Gender distribution across different age groups

«📌 Specific numerical findings can be added after reviewing the final chart outputs.»

---

👨‍💻 Author

Dinesh More

📊 Data Science / Data Analytics Project

---

📜 License

This project is licensed under the MIT License.