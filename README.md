# 🛍️ Customer Shopping Behavior — Data Cleaning and Analytics Project

A reproducible, modular project for cleaning and analyzing retail shopping behavior data.  
This repository demonstrates **data preprocessing**, **PostgreSQL integration**, and a **workspace for SQL analysis**.
---

## Project Structure

```
customer/
│
├── data/
│   ├── shopping_behavior.csv        # Raw input data
│   ├── shopping_cleaned.csv         # Cleaned output data
│
├── src/
│   ├── shopping.py                  # Main ETL (extract-clean-load) script
│
├── sql_practice_questions.md        # SQL question set for analytics practice
└── README.md
```

---

## Features

### 1. Data Cleaning and Transformation
`src/shopping.py` performs a complete cleaning pipeline:

- Normalizes column names and data types  
- Cleans string formatting (trims spaces, unifies casing)  
- Converts `Yes/No` to boolean (`True/False`)  
- Converts numeric columns safely  
- Handles missing values using median/mode imputation  
- Removes duplicates and caps outliers (1st–99th percentile)  
- Adds derived columns:  
  - `age_group` (binned age)  
  - `high_value_purchase` (top 10% by purchase amount)

Output is saved as `data/shopping_cleaned.csv`.

---

### 2. PostgreSQL Integration
The project allows seamless loading of cleaned data into a PostgreSQL database for further analysis.

**Configurable connection inside `shopping.py`:**
```python
db_config = {
    'host': 'localhost',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'password'
}
```
Upload function:
```python
upload_to_postgresql(df_clean, table_name='shopping', db_config=db_config)
```

This creates or replaces a table named `shopping` and confirms upload success.

---

### 3. SQL Practice Workspace
A dedicated folder contains ready-to-use **SQL questions and example solutions**.  
These cover key analytics topics such as aggregation, ranking, window functions, and business KPIs.

Files:
- `sql_practice_questions.md` — moderate-level queries  

Compatible with **DuckDB** and **PostgreSQL**.

---

## How to Run

### Prerequisites
- Python 3.9+  
- PostgreSQL (local or Docker)  
- Required libraries:
  ```bash
  pip install pandas numpy sqlalchemy psycopg2
  ```

### Steps
```bash
cd src
python shopping.py
```
This will:
1. Read `data/shopping_behavior.csv`  
2. Clean and standardize data  
3. Save the result as `shopping_cleaned.csv`  
4. Upload it to PostgreSQL as `shopping` table  
---

## Environment Notes

### Path Handling
`shopping.py` dynamically detects the project root to keep paths portable:
```python
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
```
Note: No hardcoded paths — works seamlessly across environments and GitHub clones.


## Future Enhancements
- Automated EDA summary (e.g., `ydata-profiling`)  
- Pipeline orchestration using Airflow or Prefect  
- Dockerfile for reproducible PostgreSQL + ETL setup  
- Extension of SQL questions into multi-table case studies  

## 👤 Author
**Jayit Ghosh**  
Data Science & Analytics Enthusiast  
Focused on end-to-end data pipelines, SQL reasoning, and data infrastructure.
---