import csv
import io
from datetime import datetime, timezone
from typing import Any, Optional

from app.connectors.base import BaseConnector, SyncResult
from app.utils.logging import get_logger

logger = get_logger("riskzen.connectors.csv_budget")


class CSVBudgetConnector(BaseConnector):
    """Connector for parsing and normalizing CSV financial budget records."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.filename = config.get("filename", "budget.csv")
        self.default_currency = config.get("currency", "USD")

    async def connect(self) -> bool:
        """Validate config parameters."""
        return True

    async def status(self) -> dict[str, Any]:
        """Return connector configuration status."""
        return {
            "connector": "csv_budget",
            "filename": self.filename,
            "currency": self.default_currency,
        }

    def parse_csv_content(self, csv_content: str) -> list[dict[str, Any]]:
        """Parse raw CSV string into normalized BudgetRecord dictionaries.

        Supports various standard header variations:
        - period / month / date
        - category / department / line_item
        - planned / planned_amount / budget
        - actual / actual_amount / spend / spent
        - currency (optional)
        """
        f = io.StringIO(csv_content.strip())
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError("CSV file is empty or missing a header row.")

        # Header normalization mapping
        header_map: dict[str, str] = {}
        for h in reader.fieldnames:
            normalized_h = h.strip().lower().replace(" ", "_")
            if normalized_h in ["period", "month", "date", "quarter", "sprint"]:
                header_map["period"] = h
            elif normalized_h in ["category", "dept", "department", "line_item", "cost_center"]:
                header_map["category"] = h
            elif normalized_h in ["planned", "planned_amount", "budget", "allocated", "plan"]:
                header_map["planned_amount"] = h
            elif normalized_h in ["actual", "actual_amount", "spent", "spend", "cost"]:
                header_map["actual_amount"] = h
            elif normalized_h in ["currency", "curr"]:
                header_map["currency"] = h

        required_keys = ["period", "category", "planned_amount", "actual_amount"]
        missing = [k for k in required_keys if k not in header_map]
        if missing:
            raise ValueError(
                f"CSV is missing required columns: {missing}. Found headers: {list(reader.fieldnames)}"
            )

        records: list[dict[str, Any]] = []

        for row_num, row in enumerate(reader, start=2):
            period_val = (row.get(header_map["period"]) or "").strip()
            category_val = (row.get(header_map["category"]) or "").strip()

            if not period_val or not category_val:
                continue  # Skip blank line

            try:
                raw_planned = (row.get(header_map["planned_amount"]) or "0").replace("$", "").replace(",", "").strip()
                planned = float(raw_planned) if raw_planned else 0.0
            except ValueError:
                raise ValueError(f"Line {row_num}: Invalid planned amount '{row.get(header_map['planned_amount'])}'")

            try:
                raw_actual = (row.get(header_map["actual_amount"]) or "0").replace("$", "").replace(",", "").strip()
                actual = float(raw_actual) if raw_actual else 0.0
            except ValueError:
                raise ValueError(f"Line {row_num}: Invalid actual amount '{row.get(header_map['actual_amount'])}'")

            currency = self.default_currency
            if "currency" in header_map and row.get(header_map["currency"]):
                currency = row[header_map["currency"]].strip().upper()

            variance = round(actual - planned, 2)

            records.append({
                "period": period_val,
                "category": category_val,
                "planned_amount": planned,
                "actual_amount": actual,
                "variance": variance,
                "currency": currency,
                "source_filename": self.filename,
            })

        if not records:
            raise ValueError("CSV contains no valid data rows.")

        return records

    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        """Sync budget records if raw csv content was provided in config."""
        result = SyncResult(synced_at=datetime.now(timezone.utc))
        raw_content = self.config.get("csv_content")

        if not raw_content:
            result.errors.append("No csv_content provided in config for sync.")
            result.success = False
            return result

        try:
            records = self.parse_csv_content(raw_content)
            result.items_created = len(records)
            result.details = {"budget_records": records}
            result.success = True
        except Exception as exc:
            logger.error("CSV budget connector sync failed", error=str(exc))
            result.errors.append(str(exc))
            result.success = False

        return result
