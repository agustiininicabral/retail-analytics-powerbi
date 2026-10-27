# Power BI report build guide

This repository includes source data, dimensional-model SQL, KPI definitions and a report specification. It does not claim to contain a finished PBIX file.

## Load and model
Run python scripts/generate_data.py, then import the four CSV files from data/raw in Power BI Desktop. Set date columns to Date, quantity to Whole number and price/discount fields to Decimal number.

For the CSV model, create one-to-many relationships: customers.customer_id to orders.customer_id; orders.order_id to order_items.order_id; products.product_id to order_items.product_id. Prefer single-direction filtering from dimensions to facts. The PostgreSQL star-schema DDL is in sql/01_schema.sql.

## DAX measures
Assuming tables use the CSV filenames:

    Gross Sales =
    SUMX(order_items, order_items[quantity] * order_items[unit_price])

    Net Sales =
    SUMX(order_items, order_items[quantity] * order_items[unit_price] * (1 - order_items[discount_pct]))

    COGS =
    SUMX(order_items, order_items[quantity] * RELATED(products[unit_cost]))

    Gross Profit = [Net Sales] - [COGS]
    Gross Margin % = DIVIDE([Gross Profit], [Net Sales])
    Orders = DISTINCTCOUNT(orders[order_id])
    Average Order Value = DIVIDE([Net Sales], [Orders])

## Report pages
1. Executive overview: Net Sales, Gross Profit, Gross Margin %, Orders and monthly trend.
2. Product performance: sales/profit by category and product, margin formatting.
3. Customer and region: segment, order region, top customers and concentration.
4. Channel performance: net sales, orders and average order value by channel.

Add date, channel, region and category slicers. Format currency and percentages consistently. Explain KPI definitions in tooltips.

## Acceptance checklist
- KPI totals reconcile to independently calculated values.
- Date filters affect intended visuals.
- No ambiguous or many-to-many relationships.
- Margin uses DIVIDE to handle zero sales.
- Synthetic-data notice is visible.
- Commit screenshots and a PBIX only after the report is actually built and reviewed.
