-- Retail Analytics Schema for PostgreSQL
-- Star schema design: fact table plus customer, product, store, and date dimensions.

DROP TABLE IF EXISTS sales_fact CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_store CASCADE;

CREATE TABLE dim_customer (
    customer_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    city VARCHAR(100),
    signup_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dim_store (
    store_id INTEGER PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    region VARCHAR(50) NOT NULL,
    manager_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    unit_cost NUMERIC(10, 2) NOT NULL CHECK (unit_cost >= 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(10) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE sales_fact (
    transaction_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES dim_customer(customer_id),
    product_id INTEGER NOT NULL REFERENCES dim_product(product_id),
    store_id INTEGER NOT NULL REFERENCES dim_store(store_id),
    sale_date DATE NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_amount NUMERIC(12, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    profit NUMERIC(12, 2) NOT NULL,
    discount_amount NUMERIC(10, 2) DEFAULT 0,
    promotion_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sale_date FOREIGN KEY (sale_date) REFERENCES dim_date(date_id)
);

CREATE INDEX idx_sales_customer ON sales_fact(customer_id);
CREATE INDEX idx_sales_product ON sales_fact(product_id);
CREATE INDEX idx_sales_store ON sales_fact(store_id);
CREATE INDEX idx_sales_date ON sales_fact(sale_date);
CREATE INDEX idx_store_region ON dim_store(region);
CREATE INDEX idx_product_category ON dim_product(category);

COMMENT ON TABLE dim_customer IS 'Customer dimension containing demographics and signup information.';
COMMENT ON TABLE dim_store IS 'Store dimension containing geography and region information.';
COMMENT ON TABLE dim_product IS 'Product dimension containing category, brand, cost, and price attributes.';
COMMENT ON TABLE dim_date IS 'Date dimension for dashboard filters and time-series analytics.';
COMMENT ON TABLE sales_fact IS 'Sales fact table containing retail transactions.';
COMMENT ON COLUMN sales_fact.profit IS 'Calculated during ETL as total_amount - quantity * product unit_cost.';
