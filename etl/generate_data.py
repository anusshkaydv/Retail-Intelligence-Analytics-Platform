import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


NUM_CUSTOMERS = 500
NUM_PRODUCTS = 200
NUM_STORES = 10
NUM_SALES = 10000
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2026, 6, 30)
RANDOM_SEED = 42

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def random_date(start_date, end_date):
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))


def generate_customers():
    cities = ["Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Pune"]
    return pd.DataFrame(
        {
            "customer_id": customer_id,
            "first_name": f"Customer_{customer_id}",
            "last_name": f"Lastname_{customer_id}",
            "email": f"customer{customer_id}@example.com",
            "city": random.choice(cities),
            "signup_date": (START_DATE - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
        }
        for customer_id in range(1, NUM_CUSTOMERS + 1)
    )


def generate_stores():
    cities = ["Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Pune"]
    regions = ["North", "South", "East", "West"]
    stores = []

    for store_id in range(1, NUM_STORES + 1):
        region = regions[(store_id - 1) % len(regions)]
        stores.append({
            "store_id": store_id,
            "store_name": f"Store_{store_id}",
            "city": random.choice(cities),
            "region": region,
            "manager_name": f"Manager_{store_id}",
        })

    return pd.DataFrame(stores)


def generate_products():
    categories = ["Electronics", "Clothing", "Home", "Books", "Toys", "Sports"]
    products = []

    for product_id in range(1, NUM_PRODUCTS + 1):
        category = random.choice(categories)
        base_price = random.uniform(5.00, 200.00)

        if category == "Electronics":
            base_price *= random.uniform(1.2, 2.0)
        elif category == "Clothing":
            base_price *= random.uniform(0.5, 1.5)

        products.append(
            {
                "product_id": product_id,
                "product_name": f"Product_{product_id}",
                "category": category,
                "brand": f"Brand_{random.randint(1, 20)}",
                "unit_cost": round(base_price * 0.6, 2),
                "unit_price": round(base_price, 2),
            }
        )

    return pd.DataFrame(products)


def generate_sales(products):
    product_lookup = products.set_index("product_id")["unit_price"].to_dict()
    sales = []

    for transaction_id in range(1, NUM_SALES + 1):
        sale_date = random_date(START_DATE, END_DATE)
        product_id = random.randint(1, NUM_PRODUCTS)
        quantity = random.randint(1, 5 if sale_date.month in [11, 12] else 3)
        unit_price = product_lookup[product_id]

        sales.append(
            {
                "transaction_id": transaction_id,
                "customer_id": random.randint(1, NUM_CUSTOMERS),
                "product_id": product_id,
                "store_id": random.randint(1, NUM_STORES),
                "date": sale_date.strftime("%Y-%m-%d"),
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": round(quantity * unit_price, 2),
            }
        )

    return pd.DataFrame(sales)


def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    DATA_DIR.mkdir(exist_ok=True)

    print("Generating customers...")
    customers = generate_customers()
    customers.to_csv(DATA_DIR / "customers.csv", index=False)

    print("Generating stores...")
    stores = generate_stores()
    stores.to_csv(DATA_DIR / "stores.csv", index=False)

    print("Generating products...")
    products = generate_products()
    products.to_csv(DATA_DIR / "products.csv", index=False)

    print("Generating sales transactions...")
    sales = generate_sales(products)
    sales.to_csv(DATA_DIR / "sales_transactions.csv", index=False)

    print(f"Generated {len(customers)} customers, {len(products)} products, {len(stores)} stores, and {len(sales)} sales.")
    print(f"CSV files saved to {DATA_DIR}")


if __name__ == "__main__":
    main()
