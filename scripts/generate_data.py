"""Generate deterministic synthetic retail CSV files."""
import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate(seed=2026, customers_count=120, orders_count=600):
    rng = random.Random(seed)
    regions = ["North", "South", "East", "West"]
    channels = ["Online", "Store", "Marketplace"]
    catalog = [
        ("P001", "Backpack", "Accessories", 28, 11),
        ("P002", "Bottle", "Accessories", 12, 4),
        ("P003", "Headphones", "Accessories", 65, 31),
        ("P004", "Lamp", "Home", 34, 14),
        ("P005", "Mug", "Home", 9, 2.5),
        ("P006", "Desk organizer", "Home", 18, 7),
        ("P007", "Keyboard", "Electronics", 48, 22),
        ("P008", "Mouse", "Electronics", 24, 9),
        ("P009", "Webcam", "Electronics", 72, 38),
    ]
    customers = [
        {"customer_id": f"C{i:04}", "region": rng.choice(regions),
         "signup_date": (date(2023, 1, 1) + timedelta(days=rng.randrange(900))).isoformat(),
         "segment": rng.choice(["Consumer", "Small Business", "Corporate"])}
        for i in range(1, customers_count + 1)
    ]
    products = [
        {"product_id": pid, "product_name": name, "category": category,
         "unit_price": price, "unit_cost": cost}
        for pid, name, category, price, cost in catalog
    ]
    orders, items = [], []
    start = date(2024, 1, 1)
    for i in range(1, orders_count + 1):
        order_id = f"O{i:05}"
        orders.append({"order_id": order_id, "customer_id": rng.choice(customers)["customer_id"],
                       "order_date": (start + timedelta(days=rng.randrange(730))).isoformat(),
                       "channel": rng.choice(channels), "region": rng.choice(regions)})
        count = rng.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
        for _ in range(count):
            product = rng.choice(products)
            items.append({"order_item_id": f"I{len(items) + 1:06}", "order_id": order_id,
                          "product_id": product["product_id"], "quantity": rng.randint(1, 5),
                          "unit_price": product["unit_price"],
                          "discount_pct": rng.choice([0, 0, 0.05, 0.1, 0.15])})
    return {"customers": customers, "products": products, "orders": orders, "order_items": items}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--customers", type=int, default=120)
    parser.add_argument("--orders", type=int, default=600)
    args = parser.parse_args()
    if args.customers < 1 or args.orders < 1:
        parser.error("--customers and --orders must be positive integers")
    for name, rows in generate(args.seed, args.customers, args.orders).items():
        write_csv(OUT / f"{name}.csv", rows)
        print(f"{name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
