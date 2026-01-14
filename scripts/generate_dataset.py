import os
import pandas as pd
import numpy as np
from datetime import datetime

np.random.seed(42)

OUT = "outputs"
STAR = os.path.join(OUT, "star_schema")
os.makedirs(OUT, exist_ok=True)
os.makedirs(STAR, exist_ok=True)

dates = pd.date_range("2025-01-01", periods=365, freq="D")
products = pd.DataFrame({
    "producto": ["Crema A","Crema B","Crema C","Perfume X","Shampoo Z","Jabón Y","Protector S","Serum K"],
    "categoria": ["Cremas","Cremas","Cremas","Perfumería","Higiene","Higiene","Dermocosmética","Dermocosmética"]
})
customers = pd.DataFrame({
    "cliente": [f"Cliente {i:03d}" for i in range(1, 151)],
    "segmento": np.random.choice(["Retail","Mayorista","Online"], size=150, p=[0.55,0.15,0.30])
})

rows = []
for _ in range(6000):
    d = np.random.choice(dates)
    p = products.sample(1).iloc[0]
    c = customers.sample(1).iloc[0]
    qty = int(np.random.randint(1, 6))
    pu = float(np.random.choice([800, 950, 1200, 1500, 1800, 2200, 2600, 3100]))
    cu = round(pu * np.random.uniform(0.45, 0.78), 2)
    rows.append([d, c["cliente"], c["segmento"], p["producto"], p["categoria"], qty, pu, cu])

raw = pd.DataFrame(rows, columns=["fecha","cliente","segmento","producto","categoria","cantidad","precio_unitario","costo_unitario"])
raw["venta"] = raw["cantidad"] * raw["precio_unitario"]
raw["costo"] = raw["cantidad"] * raw["costo_unitario"]
raw["margen"] = raw["venta"] - raw["costo"]

# save raw excel
raw_path = os.path.join(OUT, "raw_sales.xlsx")
raw.to_excel(raw_path, index=False, engine="openpyxl")

# build star schema
dim_date = raw[["fecha"]].drop_duplicates().sort_values("fecha").reset_index(drop=True)
dim_date["anio"] = dim_date["fecha"].dt.year
dim_date["mes"] = dim_date["fecha"].dt.month
dim_date["mes_nombre"] = dim_date["fecha"].dt.strftime("%b")
dim_date["date_key"] = range(1, len(dim_date)+1)

dim_product = raw[["producto","categoria"]].drop_duplicates().sort_values(["categoria","producto"]).reset_index(drop=True)
dim_product["product_key"] = range(1, len(dim_product)+1)

dim_customer = raw[["cliente","segmento"]].drop_duplicates().sort_values(["segmento","cliente"]).reset_index(drop=True)
dim_customer["customer_key"] = range(1, len(dim_customer)+1)

fact = raw.merge(dim_date[["fecha","date_key"]], on="fecha") \
          .merge(dim_product, on=["producto","categoria"]) \
          .merge(dim_customer, on=["cliente","segmento"])

fact_sales = fact[["date_key","product_key","customer_key","cantidad","precio_unitario","costo_unitario","venta","costo","margen"]]

# export csvs
dim_date.to_csv(os.path.join(STAR, "dim_date.csv"), index=False)
dim_product.to_csv(os.path.join(STAR, "dim_product.csv"), index=False)
dim_customer.to_csv(os.path.join(STAR, "dim_customer.csv"), index=False)
fact_sales.to_csv(os.path.join(STAR, "fact_sales.csv"), index=False)

print("OK - Generated dataset")
print(raw_path)
print(STAR)
