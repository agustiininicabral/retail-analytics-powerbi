# Data Dictionary

## dim_date
- date_key (int) surrogate key
- fecha (date)
- anio (int)
- mes (int)
- mes_nombre (text)

## dim_product
- product_key (int)
- producto (text)
- categoria (text)

## dim_customer
- customer_key (int)
- cliente (text)
- segmento (text)

## fact_sales
- date_key (int)
- product_key (int)
- customer_key (int)
- cantidad (int)
- precio_unitario (float)
- costo_unitario (float)
- venta (float)
- costo (float)
- margen (float)
