import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SCHEMA_FILE = PROJECT_ROOT / "sql" / "schema.sql"

def database_url():
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError(
            "Set DATABASE_URL or POSTGRES_PASSWORD before running the loader. "
            "For local use, copy .env.example to .env and export the values in your shell."
        )

    user = os.getenv("POSTGRES_USER", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5433")
    database = os.getenv("POSTGRES_DB", "retail_analytics")
    return f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/{database}"


def build_date_dimension(start_date, end_date):
    dates = pd.date_range(start_date, end_date, freq="D")
    return pd.DataFrame(
        {
            "date_id": dates.date,
            "full_date": dates.date,
            "year": dates.year,
            "quarter": dates.quarter,
            "month": dates.month,
            "month_name": dates.strftime("%B"),
            "day_of_month": dates.day,
            "day_of_week": dates.dayofweek + 1,
            "day_name": dates.strftime("%A"),
            "is_weekend": dates.dayofweek >= 5,
        }
    )


def recreate_schema(engine):
    with engine.begin() as connection:
        connection.execute(text(SCHEMA_FILE.read_text()))


def load_table(df, table_name, engine):
    df.to_sql(table_name, con=engine, if_exists="append", index=False, method="multi")
    print(f"Loaded {len(df)} rows into {table_name}.")


def load_data_to_db():
    print("Starting ETL process...")
    engine = create_engine(database_url())

    print("Recreating schema...")
    recreate_schema(engine)

    customers = pd.read_csv(DATA_DIR / "customers.csv", parse_dates=["signup_date"])
    stores = pd.read_csv(DATA_DIR / "stores.csv")
    products = pd.read_csv(DATA_DIR / "products.csv")
    sales = pd.read_csv(DATA_DIR / "sales_transactions.csv", parse_dates=["date"])

    date_dimension = build_date_dimension(sales["date"].min(), sales["date"].max())

    sales_with_cost = sales.merge(
        products[["product_id", "unit_cost"]],
        on="product_id",
        how="left",
        validate="many_to_one",
    )
    sales_with_cost["profit"] = (
        sales_with_cost["total_amount"] - (sales_with_cost["quantity"] * sales_with_cost["unit_cost"])
    ).round(2)

    sales_fact = sales_with_cost[
        [
            "transaction_id",
            "customer_id",
            "product_id",
            "store_id",
            "date",
            "quantity",
            "unit_price",
            "profit",
        ]
    ].rename(columns={"date": "sale_date"})

    load_table(customers, "dim_customer", engine)
    load_table(stores, "dim_store", engine)
    load_table(products, "dim_product", engine)
    load_table(date_dimension, "dim_date", engine)
    load_table(sales_fact, "sales_fact", engine)

    print("ETL process completed successfully.")


if __name__ == "__main__":
    load_data_to_db()
