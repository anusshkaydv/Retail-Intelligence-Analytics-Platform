-- Optional psql loader for the Docker Compose Postgres container.
-- Run after sql/schema.sql when CSV files are mounted at /data.

\copy dim_customer(customer_id, first_name, last_name, email, city, signup_date) FROM '/data/customers.csv' WITH (FORMAT csv, HEADER true);
\copy dim_store(store_id, store_name, city, region, manager_name) FROM '/data/stores.csv' WITH (FORMAT csv, HEADER true);
\copy dim_product(product_id, product_name, category, brand, unit_cost, unit_price) FROM '/data/products.csv' WITH (FORMAT csv, HEADER true);

CREATE TEMP TABLE temp_sales_transactions (
    transaction_id INTEGER,
    customer_id INTEGER,
    product_id INTEGER,
    store_id INTEGER,
    date DATE,
    quantity INTEGER,
    unit_price NUMERIC(10, 2),
    total_amount NUMERIC(12, 2)
);

\copy temp_sales_transactions FROM '/data/sales_transactions.csv' WITH (FORMAT csv, HEADER true);

INSERT INTO dim_date (
    date_id,
    full_date,
    year,
    quarter,
    month,
    month_name,
    day_of_month,
    day_of_week,
    day_name,
    is_weekend
)
SELECT
    date_day::date AS date_id,
    date_day::date AS full_date,
    EXTRACT(YEAR FROM date_day)::integer AS year,
    EXTRACT(QUARTER FROM date_day)::integer AS quarter,
    EXTRACT(MONTH FROM date_day)::integer AS month,
    TO_CHAR(date_day, 'Month') AS month_name,
    EXTRACT(DAY FROM date_day)::integer AS day_of_month,
    EXTRACT(ISODOW FROM date_day)::integer AS day_of_week,
    TO_CHAR(date_day, 'Day') AS day_name,
    EXTRACT(ISODOW FROM date_day) IN (6, 7) AS is_weekend
FROM GENERATE_SERIES(
    (SELECT MIN(date::date) FROM temp_sales_transactions),
    (SELECT MAX(date::date) FROM temp_sales_transactions),
    INTERVAL '1 day'
) AS date_day;

INSERT INTO sales_fact (
    transaction_id,
    customer_id,
    product_id,
    store_id,
    sale_date,
    quantity,
    unit_price,
    profit
)
SELECT
    s.transaction_id,
    s.customer_id,
    s.product_id,
    s.store_id,
    s.date AS sale_date,
    s.quantity,
    s.unit_price,
    ROUND(s.total_amount - (s.quantity * p.unit_cost), 2) AS profit
FROM temp_sales_transactions s
JOIN dim_product p ON s.product_id = p.product_id;
