# ruff: noqa: I001 -- the test imports repository scripts as a namespace package.
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import generate_data, validate_data



def write_dataset(data, directory):
    for name, rows in data.items():
        with (directory / f"{name}.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def run_validator(data, tmp_path, monkeypatch):
    write_dataset(data, tmp_path)
    monkeypatch.setattr(validate_data, "DATA", tmp_path)
    monkeypatch.setattr(validate_data, "REPORT", tmp_path / "report.json")
    return validate_data.validate()


def test_generator_is_deterministic():
    assert generate_data.generate(7, 5, 12) == generate_data.generate(7, 5, 12)


def test_generator_respects_requested_dimensions():
    data = generate_data.generate(3, 8, 20)
    assert len(data["customers"]) == 8
    assert len(data["products"]) == 9
    assert len(data["orders"]) == 20
    assert len(data["order_items"]) >= 20
    assert all(int(row["quantity"]) > 0 for row in data["order_items"])


def test_validator_accepts_valid_generated_data():
    data = generate_data.generate(11, 10, 25)
    with TemporaryDirectory() as directory:
        temp = Path(directory)
        for name, rows in data.items():
            with (temp / f"{name}.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        old_data, old_report = validate_data.DATA, validate_data.REPORT
        validate_data.DATA, validate_data.REPORT = temp, temp / "report.json"
        try:
            result = validate_data.validate()
        finally:
            validate_data.DATA, validate_data.REPORT = old_data, old_report
    assert result["status"] == "PASS"
    assert result["failure_count"] == 0


def test_validator_rejects_non_finite_product_values_and_invalid_line_prices(
    tmp_path, monkeypatch
):
    data = generate_data.generate(17, 10, 25)
    data["products"][0]["unit_price"] = float("nan")
    data["order_items"][0]["unit_price"] = -1

    result = run_validator(data, tmp_path, monkeypatch)

    assert result["status"] == "FAIL"
    assert any("non-finite price/cost" in failure for failure in result["failures"])
    assert any("invalid unit_price" in failure for failure in result["failures"])


def test_validator_rejects_order_line_price_that_differs_from_catalog(
    tmp_path, monkeypatch
):
    data = generate_data.generate(19, 10, 25)
    item = data["order_items"][0]
    item["unit_price"] = float(item["unit_price"]) + 1

    result = run_validator(data, tmp_path, monkeypatch)

    assert result["status"] == "FAIL"
    assert any("unit_price does not match product" in failure for failure in result["failures"])


def test_validator_trims_headers_and_values_for_relationship_checks(tmp_path, monkeypatch):
    data = generate_data.generate(23, 10, 25)
    write_dataset(data, tmp_path)
    customers_path = tmp_path / "customers.csv"
    with customers_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    rows[0][0] = " customer_id "
    rows[1][0] = f" {rows[1][0]} "
    with customers_path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)

    result = run_validator(data, tmp_path, monkeypatch)

    assert result["status"] == "PASS"
    assert result["failure_count"] == 0


def test_validator_rejects_duplicate_headers_after_trimming(tmp_path, monkeypatch):
    data = generate_data.generate(29, 10, 25)
    write_dataset(data, tmp_path)
    products_path = tmp_path / "products.csv"
    with products_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    rows[0][1] = " product_id "
    with products_path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)

    result = run_validator(data, tmp_path, monkeypatch)

    assert result["status"] == "FAIL"
    assert any("duplicate columns after trimming" in failure for failure in result["failures"])


def test_validator_rejects_orphan_customer_and_invalid_discount(
    tmp_path, monkeypatch
):
    data = generate_data.generate(31, 10, 25)
    data["orders"][0]["customer_id"] = "C99999"
    data["order_items"][0]["discount_pct"] = 1.0

    result = run_validator(data, tmp_path, monkeypatch)

    assert result["status"] == "FAIL"
    assert any("unknown customer C99999" in failure for failure in result["failures"])
    assert any("invalid discount" in failure for failure in result["failures"])


def test_validator_main_returns_nonzero_for_invalid_dataset(tmp_path, monkeypatch):
    data = generate_data.generate(37, 10, 25)
    data["order_items"][0]["discount_pct"] = 1.0
    write_dataset(data, tmp_path)
    monkeypatch.setattr(validate_data, "DATA", tmp_path)
    monkeypatch.setattr(validate_data, "REPORT", tmp_path / "report.json")

    assert validate_data.main() == 1
    report = (tmp_path / "report.json").read_text(encoding="utf-8")
    assert '"status": "FAIL"' in report
