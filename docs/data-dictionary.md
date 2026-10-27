# Data dictionary

All records are synthetic. A seeded pseudo-random generator makes the dataset reproducible.

| File | Grain | Description |
|---|---|---|
| customers.csv | One row per customer | Segment, customer region, signup date |
| products.csv | One row per product | Category, list price, unit cost |
| orders.csv | One row per order | Customer, order date, channel, order region |
| order_items.csv | One row per order line | Product, quantity, unit price, discount rate |

Definitions:
- unit_price: synthetic unit selling price before discount.
- unit_cost: estimated unit cost for gross-profit calculations.
- discount_pct: fractional discount in the range [0, 1); 0.10 means 10%.
- gross_sales: quantity multiplied by unit price.
- net_sales: gross sales multiplied by (1 minus discount_pct).
- gross_profit: net sales minus quantity multiplied by unit cost.

Order region is intentionally stored separately from customer region: they represent different business attributes.
