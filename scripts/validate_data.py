"""Validate the synthetic retail CSV dataset and write a JSON report."""
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw"
REPORT = ROOT / "reports" / "data_quality_report.json"


def read_csv(name):
    path = DATA / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate():
    customers, products = read_csv("customers"), read_csv("products")
    orders, items = read_csv("orders"), read_csv("order_items")
    failures = []

    def unique(rows, key, table):
        values = [row.get(key, "") for row in rows]
        if any(not value for value in values):
            failures.append(f"{table}.{key}: blank key")
        if len(values) != len(set(values)):
            failures.append(f"{table}.{key}: duplicate key")

    unique(customers, "customer_id", "customers")
    unique(products, "product_id", "products")
    unique(orders, "order_id", "orders")
    unique(items, "order_item_id", "order_items")
    customer_ids = {r["customer_id"] for r in customers}
    product_ids = {r["product_id"] for r in products}
    order_ids = {r["order_id"] for r in orders}

    for row in orders:
        if row["customer_id"] not in customer_ids:
            failures.append(f"orders: unknown customer {row['customer_id']}")
        try:
            date.fromisoformat(row["order_date"])
        except ValueError:
            failures.append(f"orders: invalid date {row['order_date']}")
        if row["channel"] not in {"Online", "Store", "Marketplace"}:
            failures.append(f"orders: invalid channel {row['channel']}")

    for row in products:
        try:
            if float(row["unit_price"]) <= 0 or float(row["unit_cost"]) < 0:
                failures.append(f"products: invalid price/cost {row['product_id']}")
        except ValueError:
            failures.append(f"products: non-numeric price/cost {row['product_id']}")

    for row in items:
        if row["order_id"] not in order_ids:
            failures.append(f"order_items: unknown order {row['order_id']}")
        if row["product_id"] not in product_ids:
            failures.append(f"order_items: unknown product {row['product_id']}")
        try:
            if int(row["quantity"]) <= 0:
                failures.append(f"order_items: invalid quantity {row['order_item_id']}")
            if not 0 <= float(row["discount_pct"]) < 1:
                failures.append(f"order_items: invalid discount {row['order_item_id']}")
        except ValueError:
            failures.append(f"order_items: invalid numeric value {row['order_item_id']}")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "row_counts": {"customers": len(customers), "products": len(products),
                       "orders": len(orders), "order_items": len(items)},
        "failure_count": len(failures), "failures": failures,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    report = validate()
    total_rows = sum(report["row_counts"].values())
    print(
        f"{report['status']}: {total_rows} rows; "
        f"{report['failure_count']} failures"
    )
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
