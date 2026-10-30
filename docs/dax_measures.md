# DAX measures for the CSV Power BI model

Import the four generated CSV files as tables named `customers`, `products`, `orders`, and `order_items`. Create the relationships below before adding these measures:

- `customers[customer_id]` (1) → `orders[customer_id]` (*)
- `orders[order_id]` (1) → `order_items[order_id]` (*)
- `products[product_id]` (1) → `order_items[product_id]` (*)
- `Date[Date]` (1) → `orders[order_date]` (*)

Use single-direction filtering from dimensions to facts. Set `orders[order_date]` to Date type.

## Date table

Create this calculated table:

```dax
Date =
CALENDAR (
    MIN ( orders[order_date] ),
    MAX ( orders[order_date] )
)
```

Add calculated columns:

```dax
Year = YEAR ( 'Date'[Date] )
Month Number = MONTH ( 'Date'[Date] )
Month = FORMAT ( 'Date'[Date], "MMM" )
Year Month = FORMAT ( 'Date'[Date], "YYYY-MM" )
```

Sort `Date[Month]` by `Date[Month Number]`, and `Date[Year Month]` by a numeric YearMonth sort column if you add one. Mark `Date` as the model's date table using `Date[Date]`.

## Core measures

```dax
Gross Sales =
SUMX (
    order_items,
    order_items[quantity] * order_items[unit_price]
)

Discount Amount =
[Gross Sales] - [Net Sales]

Net Sales =
SUMX (
    order_items,
    order_items[quantity]
        * order_items[unit_price]
        * ( 1 - order_items[discount_pct] )
)

COGS =
SUMX (
    order_items,
    order_items[quantity] * RELATED ( products[unit_cost] )
)

Gross Profit =
[Net Sales] - [COGS]

Gross Margin % =
DIVIDE ( [Gross Profit], [Net Sales] )

Orders =
DISTINCTCOUNT ( orders[order_id] )

Average Order Value =
DIVIDE ( [Net Sales], [Orders] )

Units Sold =
SUM ( order_items[quantity] )

Average Selling Price =
DIVIDE ( [Net Sales], [Units Sold] )
```

Format sales, discount, COGS, profit and average order value as currency. Format margin as percentage.

## Time intelligence

```dax
Net Sales Previous Month =
CALCULATE ( [Net Sales], DATEADD ( 'Date'[Date], -1, MONTH ) )

Net Sales MoM Change =
[Net Sales] - [Net Sales Previous Month]

Net Sales MoM % =
DIVIDE ( [Net Sales MoM Change], [Net Sales Previous Month] )

Net Sales Previous Year =
CALCULATE ( [Net Sales], DATEADD ( 'Date'[Date], -1, YEAR ) )

Net Sales YoY Change =
[Net Sales] - [Net Sales Previous Year]

Net Sales YoY % =
DIVIDE ( [Net Sales YoY Change], [Net Sales Previous Year] )

Net Sales Rolling 30D =
CALCULATE (
    [Net Sales],
    DATESINPERIOD ( 'Date'[Date], MAX ( 'Date'[Date] ), -30, DAY )
)
```

Time-intelligence measures require the Date relationship to be active and the Date table to be marked correctly. Percent changes return blank when the comparison period is zero or unavailable.

## Product ranking

```dax
Product Sales Rank =
RANKX (
    ALLSELECTED ( products[product_name] ),
    [Net Sales],
    ,
    DESC,
    DENSE
)
```

Use the rank in a product table or apply a Top N visual filter. These measures are designed for the CSV relationship model in `docs/power-bi-build.md`; they are not written against the separate PostgreSQL star schema.
