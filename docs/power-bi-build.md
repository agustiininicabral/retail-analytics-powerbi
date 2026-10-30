# Power BI report build guide

This repository includes reproducible source data, data-quality validation, dimensional-model SQL, KPI definitions and a Power BI report specification. It does **not** contain a finished PBIX file.

## 1. Generate and validate the source data

From the repository root:

```powershell
python scripts/generate_data.py
python scripts/validate_data.py
python -m pytest -q
```

Import the four CSVs from `data/raw/` into Power BI Desktop: `customers.csv`, `products.csv`, `orders.csv`, and `order_items.csv`. Rename the imported tables to match the filenames without extensions.

Set `signup_date` and `order_date` to Date, IDs and names to Text, `quantity` to Whole number, and prices, costs and discounts to Decimal number. Confirm `discount_pct` is stored as a decimal fraction (for example, 0.10 means 10%).

## 2. Create the model

Create these active one-to-many relationships, with single-direction filtering from the one side to the many side:

| One side | Many side |
|---|---|
| customers[customer_id] | orders[customer_id] |
| orders[order_id] | order_items[order_id] |
| products[product_id] | order_items[product_id] |
| Date[Date] | orders[order_date] |

Create the Date table and its columns as described in [dax_measures.md](dax_measures.md). Mark it as the date table. Do not create a direct customers-to-order_items relationship.

The PostgreSQL star-schema alternative is documented in `sql/01_schema.sql`; it is a separate model and should not be mixed with the CSV relationship layout.

## 3. Add measures

Use the definitions in [dax_measures.md](dax_measures.md). They cover gross sales, discounts, net sales, COGS, gross profit, gross margin, distinct orders, average order value, units sold, average selling price, MoM/YoY changes, rolling 30-day sales and product ranking.

The measures calculate line-level revenue from quantity, unit price and discount. COGS uses the product catalog's unit cost. Average order value divides net sales by distinct order IDs; it is not an average of individual line items.

## 4. Build report pages

1. **Executive overview:** Net Sales, Gross Profit, Gross Margin %, Orders, Average Order Value and monthly net-sales trend.
2. **Product performance:** Net Sales and Gross Profit by category/product, top products, margin percentage.
3. **Customer and region:** customer segment, region, top customers and revenue concentration.
4. **Channel performance:** Net Sales, Orders and Average Order Value by channel.

Add date, channel, region, category and customer-segment slicers. Use consistent currency/percentage formatting, descriptive titles, and tooltips explaining KPI definitions. Use a clear report title and display the synthetic-data notice.

## 5. Reconciliation and acceptance

- Net Sales equals the sum of quantity × unit price × (1 − discount_pct) across order lines.
- Gross Profit equals Net Sales less COGS.
- Orders counts distinct order IDs, not order lines.
- Average Order Value equals Net Sales divided by distinct Orders.
- Date slicers affect the intended visuals and time-intelligence measures.
- Product and customer filters propagate through the intended relationships.
- No ambiguous or many-to-many relationships are present.
- Gross Margin % uses DIVIDE and handles zero net sales.
- Report totals reconcile with independent calculations from the source CSVs.
- Synthetic-data notice is visible.

Commit screenshots and a PBIX only after the report has actually been assembled, refreshed, reconciled and reviewed in Power BI Desktop. Do not describe the specification as a completed Power BI report.
