'''
Short summary:
- Script to clean a shopping-behavior CSV, save a cleaned CSV, and upload the cleaned table to a PostgreSQL database.

What it does (high level):
- Reads raw data from data/shopping_behavior.csv.
- Runs a robust cleaning pipeline (normalize column names, trim strings, standardize booleans, convert numeric/int types, handle missing values, drop duplicates, cap outliers, normalize categorical values, convert to category dtype).
- Adds derived columns (age_group, high_value_purchase).
- Writes the cleaned data to data/shopping_cleaned.csv.
- Uploads the cleaned DataFrame to a PostgreSQL table using SQLAlchemy.

Key functions:
- clean_shopping_data(df): returns a cleaned and typed DataFrame with derived features and outlier handling.
- upload_to_postgresql(df, table_name, db_config): writes the DataFrame to PostgreSQL (if_exists='replace') using credentials in db_config.

Inputs / outputs:
- Input: data/shopping_behavior.csv (raw CSV).
- Output: data/shopping_cleaned.csv (cleaned CSV) and a PostgreSQL table named 'shopping' (configurable).

Dependencies:
- pandas, numpy, pathlib, SQLAlchemy, and a running PostgreSQL instance reachable via db_config.

How to run:
- Execute the script directly (python shopping.py) after updating db_config and ensuring the data files and PostgreSQL are accessible.
'''

from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import sys

# Get absolute path of script
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths relative to project root
DATA_DIR = BASE_DIR / "data"
RAW_DATA = DATA_DIR / "shopping_behavior.csv"
CLEAN_DATA = DATA_DIR / "shopping_cleaned.csv"

# Database connection details
db_config = {
    'host': 'localhost',      
    'port': '5432',           
    'database': 'postgres',
    'user': 'postgres',
    'password': 'password'
}

TABLE_NAME = 'shopping'


def clean_shopping_data(df):      
    df_clean = df.copy()

    # 1) Normalize column names (if any stray differences)
    df_clean.columns = [c.strip().lower().replace(' ', '_').replace('(usd)', 'usd').replace('(', '').replace(')', '') for c in df_clean.columns]

    # 2) Strip whitespace from string columns
    obj_cols = df_clean.select_dtypes(include='object').columns
    for c in obj_cols:
        df_clean[c] = df_clean[c].astype(str).str.strip()

    # 3) Standardize boolean-like columns to True/False
    bool_cols = ['subscription_status', 'discount_applied', 'promo_code_used']
    for c in bool_cols:
        if c in df_clean.columns:
            df_clean[c] = df_clean[c].str.lower().map({'yes': True, 'no': False, 'true': True, 'false': False}).fillna(df_clean[c])

    # 4) Numeric conversions and renaming
    if 'purchase_amount_usd' not in df_clean.columns and 'purchase_amount__usd_' in df_clean.columns:
        df_clean.rename(columns={'purchase_amount__usd_': 'purchase_amount_usd'}, inplace=True)

    if 'purchase_amount_usd' in df_clean.columns:
        df_clean['purchase_amount_usd'] = pd.to_numeric(df_clean['purchase_amount_usd'].astype(str).str.replace(r'[^0-9.\-]', '', regex=True), errors='coerce')

    if 'review_rating' in df_clean.columns:
        df_clean['review_rating'] = pd.to_numeric(df_clean['review_rating'], errors='coerce')

    int_cols = ['customer_id', 'age', 'previous_purchases']
    for c in int_cols:
        if c in df_clean.columns:
            df_clean[c] = pd.to_numeric(df_clean[c], errors='coerce').astype('Int64')

    # 5) Handle missing values
    # Numeric: fill with median; Categorical: fill with mode
    for c in df_clean.columns:
        if pd.api.types.is_numeric_dtype(df_clean[c]):
            median = df_clean[c].median()
            df_clean[c] = df_clean[c].fillna(median)
        else:
            # if entire column is NaNs or empty string, leave as is
            if df_clean[c].mode(dropna=True).shape[0] > 0:
                df_clean[c] = df_clean[c].replace({'nan': None}).fillna(df_clean[c].mode(dropna=True)[0])

    # 6) Remove exact duplicates
    df_clean = df_clean.drop_duplicates()

    # 7) Cap outliers in purchase_amount_usd at 1st/99th percentiles
    if 'purchase_amount_usd' in df_clean.columns:
        p1, p99 = df_clean['purchase_amount_usd'].quantile([0.01, 0.99])
        df_clean['purchase_amount_usd'] = df_clean['purchase_amount_usd'].clip(lower=p1, upper=p99)

    # 8) Standardize some categorical values
    if 'gender' in df_clean.columns:
        df_clean['gender'] = df_clean['gender'].str.lower().map({'male': 'Male', 'female': 'Female', 'm': 'Male', 'f': 'Female'}).fillna(df_clean['gender'])

    # Standardize frequency_of_purchases
    freq_map = {
        'weekly': 'Weekly', 'week': 'Weekly',
        'fortnightly': 'Bi-Weekly', 'bi-weekly': 'Bi-Weekly', 'biweekly': 'Bi-Weekly',
        'monthly': 'Monthly', 'annually': 'Annually', 'annual': 'Annually',
        'quarterly': 'Quarterly', 'biweekly ': 'Bi-Weekly'
    }
    if 'frequency_of_purchases' in df_clean.columns:
        df_clean['frequency_of_purchases'] = df_clean['frequency_of_purchases'].str.lower().map(freq_map).fillna(df_clean['frequency_of_purchases'])

    # 9) Convert appropriate columns to category dtype to save memory
    cat_cols = ['gender', 'category', 'location', 'size', 'color', 'season',
                'shipping_type', 'payment_method', 'frequency_of_purchases']
    for c in cat_cols:
        if c in df_clean.columns:
            df_clean[c] = df_clean[c].astype('category')

    # 10) Create useful derived columns
    # age_group
    if 'age' in df_clean.columns:
        bins = [0, 17, 25, 35, 50, 65, 120]
        labels = ['<18', '18-25', '26-35', '36-50', '51-65', '65+']
        df_clean['age_group'] = pd.cut(df_clean['age'].astype(float), bins=bins, labels=labels, include_lowest=True)

    # high_value flag
    if 'purchase_amount_usd' in df_clean.columns:
        threshold = df_clean['purchase_amount_usd'].quantile(0.90)
        df_clean['high_value_purchase'] = df_clean['purchase_amount_usd'] >= threshold

    # 11) Final housekeeping: reset index and ensure consistent dtypes
    df = df_clean.reset_index(drop=True)

    return df

def upload_to_postgresql(df, table_name, db_config):
    """
    Upload a DataFrame to a PostgreSQL database.

    Args:   
        df (DataFrame): The DataFrame to upload.
        table_name (str): The name of the table to create or replace.
        db_config (dict): A dictionary with database connection parameters.
    """    

    # Create the database connection URL
    connection_url = (
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )

    # Create a SQLAlchemy engine
    engine = create_engine(connection_url)

    # Upload the DataFrame to the database
    try:
        df.to_sql(table_name, engine, index=False, if_exists='replace')
        print(f"Data uploaded successfully to table '{table_name}'.")
    except Exception as e:
        print(f"Error uploading data: {e}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    
    # Read raw data
    df = pd.read_csv(RAW_DATA)    

    ## Clean data
    df_clean = clean_shopping_data(df)       

    ## Write cleaned data to CSV
    df_clean.to_csv(CLEAN_DATA, index=False)

    ## Upload cleaned data to PostgreSQL
    upload_to_postgresql(df_clean, table_name=TABLE_NAME, db_config=db_config)
