import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def load_product_prices():
    with (DATA_DIR / "products.csv").open(newline="") as file:
        return {
            row["product_id"]: round(float(row["unit_price"]), 2)
            for row in csv.DictReader(file)
        }


def main():
    product_prices = load_product_prices()
    transaction_ids = set()
    duplicate_ids = 0
    price_mismatches = 0
    sales_rows = 0
    total_revenue = 0.0

    with (DATA_DIR / "sales_transactions.csv").open(newline="") as file:
        for row in csv.DictReader(file):
            sales_rows += 1
            transaction_id = row["transaction_id"]

            if transaction_id in transaction_ids:
                duplicate_ids += 1
            transaction_ids.add(transaction_id)

            unit_price = round(float(row["unit_price"]), 2)
            if unit_price != product_prices[row["product_id"]]:
                price_mismatches += 1

            total_revenue += float(row["total_amount"])

    print(f"sales rows={sales_rows}")
    print(f"duplicate transaction ids={duplicate_ids}")
    print(f"price mismatches={price_mismatches}")
    print(f"total revenue={total_revenue:.2f}")

    if duplicate_ids or price_mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
