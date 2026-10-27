-- 1. Monthly revenue, COGS, gross profit and gross margin.
SELECT d.year, d.month, d.month_name, SUM(f.net_sales) AS net_sales,
       SUM(f.quantity * p.unit_cost) AS cogs,
       SUM(f.net_sales) - SUM(f.quantity * p.unit_cost) AS gross_profit,
       ROUND(100 * (SUM(f.net_sales) - SUM(f.quantity * p.unit_cost))
             / NULLIF(SUM(f.net_sales), 0), 2) AS gross_margin_pct
FROM retail.fact_sales f
JOIN retail.dim_order o ON o.order_key = f.order_key
JOIN retail.dim_date d ON d.date_key = o.order_date_key
JOIN retail.dim_product p ON p.product_key = f.product_key
GROUP BY d.year, d.month, d.month_name ORDER BY d.year, d.month;

-- 2. Category contribution.
SELECT p.category, SUM(f.net_sales) AS net_sales,
       SUM(f.quantity * p.unit_cost) AS cogs,
       SUM(f.net_sales) - SUM(f.quantity * p.unit_cost) AS gross_profit
FROM retail.fact_sales f JOIN retail.dim_product p ON p.product_key = f.product_key
GROUP BY p.category ORDER BY gross_profit DESC;

-- 3. Channel performance and average order value.
WITH order_totals AS (
  SELECT o.order_key, o.channel, SUM(f.net_sales) AS order_net_sales
  FROM retail.dim_order o JOIN retail.fact_sales f ON f.order_key = o.order_key
  GROUP BY o.order_key, o.channel
)
SELECT channel, COUNT(*) AS orders, SUM(order_net_sales) AS net_sales,
       ROUND(AVG(order_net_sales), 2) AS average_order_value
FROM order_totals GROUP BY channel ORDER BY net_sales DESC;

-- 4. Top ten customers.
SELECT c.customer_id, c.segment, c.region, SUM(f.net_sales) AS net_sales,
       COUNT(DISTINCT o.order_key) AS order_count
FROM retail.fact_sales f
JOIN retail.dim_order o ON o.order_key = f.order_key
JOIN retail.dim_customer c ON c.customer_key = o.customer_key
GROUP BY c.customer_id, c.segment, c.region
ORDER BY net_sales DESC LIMIT 10;
