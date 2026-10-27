"""Validate synthetic retail source data and write a machine-readable report."""

from __future__ import annotations

import csv
import json
import math
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw"
REPORT = ROOT / "reports" / "data_quality_report.json"

REQUIRED_COLUMNS = {
    "customers": {"customer_id", "region", "signup_date", "segment"},
    "products": {"product_id", "product_name", "category", "unit_price", "unit_cost"},
    "orders": {"order_id", "customer_id", "order_date", "channel", "region"},
    "order_items": {
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount_pct",
    },
}
CHANNELS = {"Online", "Store", "Marketplace"}
REGIONS = {"North", "South", "East", "West"}


def read_csv(name: str) -> list[dict[str, str]]:
    """Read a required CSV and reject missing headers or required columns."""
    path = DATA / f"{name}.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Missing required input: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        if not columns:
            raise ValueError(f"{name}.csv has no header")
        missing = sorted(REQUIRED_COLUMNS[name] - columns)
        if missing:
            raise ValueError(f"{name}.csv is missing required columns: {', '.join(missing)}")
        return list(reader)


def validate() -> dict[str, Any]:
    """Validate identifiers, relationships, dates, and numeric business rules."""
    failures: list[str] = []
    try:
        customers = read_csv("customers")
        products = read_csv("products")
        orders = read_csv("orders")
        items = read_csv("order_items")
    except (OSError, ValueError) as error:
        failures.append(str(error))
        customers, products, orders, items = [], [], [], []

    def unique(rows: list[dict[str, str]], key: str, table: str) -> None:
        values = [(row.get(key) or "").strip() for row in rows]
        if any(not value for value in values):
            failures.append(f"{table}.{key}: blank key")
        if len(values) != len(set(values)):
            failures.append(f"{table}.{key}: duplicate key")

    if not failures:
        unique(customers, "customer_id", "customers")
        unique(products, "product_id", "products")
        unique(orders, "order_id", "orders")
        unique(items, "order_item_id", "order_items")

        customer_ids = {row["customer_id"] for row in customers}
        product_by_id: dict[str, dict[str, str]] = {
            row["product_id"]: row for row in products
        }
        product_ids = set(product_by_id)
        order_ids = {row["order_id"] for row in orders}

        if not customers or not products or not orders or not items:
            failures.append("Required tables must contain at least one data row.")

        for row in customers:
            try:
                date.fromisoformat(row["signup_date"])
            except (TypeError, ValueError):
                failures.append(
                    f"customers: invalid signup_date for {row['customer_id']}"
                )
            if row["region"] not in REGIONS:
                failures.append(f"customers: invalid region {row['region']}")

        valid_product_prices: dict[str, float] = {}
        for row in products:
            product_id = row["product_id"]
            try:
                price = float(row["unit_price"])
                cost = float(row["unit_cost"])
                if not math.isfinite(price) or not math.isfinite(cost):
                    failures.append(f"products: non-finite price/cost {product_id}")
                    continue
                if price <= 0 or cost < 0:
                    failures.append(f"products: invalid price/cost {product_id}")
                    continue
                valid_product_prices[product_id] = price
            except (TypeError, ValueError):
                failures.append(f"products: non-numeric price/cost {product_id}")

        for row in orders:
            order_id = row["order_id"]
            if row["customer_id"] not in customer_ids:
                failures.append(f"orders: unknown customer {row['customer_id']}")
            try:
                date.fromisoformat(row["order_date"])
            except (TypeError, ValueError):
                failures.append(f"orders: invalid date {row['order_date']} for {order_id}")
            if row["channel"] not in CHANNELS:
                failures.append(f"orders: invalid channel {row['channel']}")
            if row["region"] not in REGIONS:
                failures.append(f"orders: invalid region {row['region']}")

        for row in items:
            item_id = row["order_item_id"]
            product_id = row["product_id"]
            if row["order_id"] not in order_ids:
                failures.append(f"order_items: unknown order {row['order_id']}")
            if product_id not in product_ids:
                failures.append(f"order_items: unknown product {product_id}")

            try:
                quantity = int(row["quantity"])
                price = float(row["unit_price"])
                discount = float(row["discount_pct"])
                if quantity <= 0:
                    failures.append(f"order_items: invalid quantity {item_id}")
                if not math.isfinite(price) or price <= 0:
                    failures.append(f"order_items: invalid unit_price {item_id}")
                if not math.isfinite(discount) or not 0 <= discount < 1:
                    failures.append(f"order_items: invalid discount {item_id}")
                expected_price = valid_product_prices.get(product_id)
                if expected_price is not None and math.isfinite(price):
                    if not math.isclose(price, expected_price, rel_tol=0, abs_tol=0.005):
                        failures.append(
                            "order_items: unit_price does not match product "
                            f"{product_id} ({item_id})"
                        )
            except (TypeError, ValueError, OverflowError):
                failures.append(f"order_items: invalid numeric value {item_id}")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "row_counts": {
            "customers": len(customers),
            "products": len(products),
            "orders": len(orders),
            "order_items": len(items),
        },
        "failure_count": len(failures),
        "failures": failures,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = validate()
    total_rows = sum(report["row_counts"].values())
    print(f"{report['status']}: {total_rows} rows; {report['failure_count']} failures")
    for failure in report["failures"]:
        print(f"- {failure}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
