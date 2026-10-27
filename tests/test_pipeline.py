import csv
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_data  # noqa: E402
import validate_data  # noqa: E402


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
