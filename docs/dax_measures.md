# DAX Measures (sugeridas)

## Base
**Ventas** =
SUM ( fact_sales[venta] )

**Costo** =
SUM ( fact_sales[costo] )

**Margen** =
SUM ( fact_sales[margen] )

**Margen %** =
DIVIDE ( [Margen], [Ventas] )

**Ticket Promedio** =
AVERAGEX ( fact_sales, fact_sales[venta] )

## Time intelligence (requiere marcar dim_date como tabla de fechas)
**Ventas MoM** =
VAR Prev = CALCULATE ( [Ventas], DATEADD ( dim_date[fecha], -1, MONTH ) )
RETURN [Ventas] - Prev

**Ventas YoY** =
VAR Prev = CALCULATE ( [Ventas], DATEADD ( dim_date[fecha], -1, YEAR ) )
RETURN [Ventas] - Prev

**Ventas Rolling 30D** =
CALCULATE ( [Ventas], DATESINPERIOD ( dim_date[fecha], MAX ( dim_date[fecha] ), -30, DAY ) )

## TopN (usarlo con visual)
**Rank Producto por Ventas** =
RANKX ( ALL ( dim_product[producto] ), [Ventas], , DESC )
