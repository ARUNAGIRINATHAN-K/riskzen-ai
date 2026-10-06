import pytest
from app.connectors.csv_budget import CSVBudgetConnector


def test_valid_csv_parsing():
    """Test parsing standard CSV budget rows."""
    connector = CSVBudgetConnector({"filename": "test_budget.csv", "currency": "USD"})

    csv_data = """period,category,planned,actual
2026-10,Engineering,50000,54000
2026-10,Cloud Infrastructure,8000,7500
2026-11,Engineering,50000,48000
"""
    records = connector.parse_csv_content(csv_data)

    assert len(records) == 3
    assert records[0]["period"] == "2026-10"
    assert records[0]["category"] == "Engineering"
    assert records[0]["planned_amount"] == 50000.0
    assert records[0]["actual_amount"] == 54000.0
    assert records[0]["variance"] == 4000.0
    assert records[0]["currency"] == "USD"

    # Infrastructure record
    assert records[1]["category"] == "Cloud Infrastructure"
    assert records[1]["variance"] == -500.0


def test_alternate_header_variations():
    """Test header alias normalization (month, spend, budget, etc.)."""
    connector = CSVBudgetConnector({})
    csv_data = """month,department,budget,spend,curr
2026-Q4,Mobile Team,$30,000,$35,500,EUR
"""
    records = connector.parse_csv_content(csv_data)
    assert len(records) == 1
    assert records[0]["period"] == "2026-Q4"
    assert records[0]["category"] == "Mobile Team"
    assert records[0]["planned_amount"] == 30000.0
    assert records[0]["actual_amount"] == 35500.0
    assert records[0]["variance"] == 5500.0
    assert records[0]["currency"] == "EUR"


def test_missing_required_headers_raises_error():
    """Test that missing required columns raises descriptive ValueError."""
    connector = CSVBudgetConnector({})
    csv_bad = """category,actual
Engineering,50000
"""
    with pytest.raises(ValueError, match="CSV is missing required columns"):
        connector.parse_csv_content(csv_bad)


def test_malformed_number_raises_error():
    """Test that invalid numerical amounts raise ValueError."""
    connector = CSVBudgetConnector({})
    csv_bad = """period,category,planned,actual
2026-10,Engineering,NOT_A_NUMBER,50000
"""
    with pytest.raises(ValueError, match="Invalid planned amount"):
        connector.parse_csv_content(csv_bad)
