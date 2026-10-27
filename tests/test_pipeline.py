import csv
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_data  # noqa: E402
import validate_data  # noqa: E402



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
