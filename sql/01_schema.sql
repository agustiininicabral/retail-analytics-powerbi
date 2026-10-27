-- PostgreSQL dimensional model for synthetic retail analytics.
CREATE SCHEMA IF NOT EXISTS retail;
CREATE TABLE IF NOT EXISTS retail.dim_customer (
  customer_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id VARCHAR(16) NOT NULL UNIQUE,
  region VARCHAR(32) NOT NULL,
  signup_date DATE NOT NULL,
  segment VARCHAR(32) NOT NULL
);
CREATE TABLE IF NOT EXISTS retail.dim_product (
  product_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  product_id VARCHAR(16) NOT NULL UNIQUE,
  product_name VARCHAR(100) NOT NULL,
  category VARCHAR(50) NOT NULL,
  unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price > 0),
  unit_cost NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0)
);
CREATE TABLE IF NOT EXISTS retail.dim_date (
  date_key INTEGER PRIMARY KEY,
  calendar_date DATE NOT NULL UNIQUE,
  year SMALLINT NOT NULL,
  quarter SMALLINT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
  month SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
  month_name VARCHAR(12) NOT NULL
);
CREATE TABLE IF NOT EXISTS retail.dim_order (
  order_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id VARCHAR(16) NOT NULL UNIQUE,
  customer_key BIGINT NOT NULL REFERENCES retail.dim_customer(customer_key),
  order_date_key INTEGER NOT NULL REFERENCES retail.dim_date(date_key),
  channel VARCHAR(32) NOT NULL,
  region VARCHAR(32) NOT NULL
);
CREATE TABLE IF NOT EXISTS retail.fact_sales (
  sales_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_key BIGINT NOT NULL REFERENCES retail.dim_order(order_key),
  product_key BIGINT NOT NULL REFERENCES retail.dim_product(product_key),
  order_item_id VARCHAR(16) NOT NULL UNIQUE,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price > 0),
  discount_pct NUMERIC(5,4) NOT NULL CHECK (discount_pct >= 0 AND discount_pct < 1),
  gross_sales NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
  net_sales NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount_pct)) STORED
);
CREATE INDEX IF NOT EXISTS ix_fact_sales_order_key ON retail.fact_sales(order_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_product_key ON retail.fact_sales(product_key);
CREATE INDEX IF NOT EXISTS ix_dim_order_date_key ON retail.dim_order(order_date_key);
