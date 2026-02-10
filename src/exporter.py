import csv
import json
from typing import Any
from src.settings import DATA_DIR
from loguru import logger


class Exporter:
    @staticmethod
    def append_to_csv(item: Any, filename: str = "live_results.csv"):
        """Append a single record to a CSV file (works with any Pydantic model)"""
        filepath = DATA_DIR / filename
        file_exists = filepath.exists()

        try:
            # Use model_dump() to convert Pydantic object to a dictionary
            row = item.model_dump()
            fieldnames = row.keys()

            with open(filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
        except Exception as e:
            logger.error(f"❌ Error while appending to CSV: {e}")

    @staticmethod
    def to_csv(data: list[Any], filename: str = "results.csv"):
        """Save the entire list of objects to a CSV file"""
        if not data:
            logger.warning("⚠️ No data available for CSV export.")
            return

        filepath = DATA_DIR / filename
        try:
            fieldnames = data[0].model_dump().keys()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in data:
                    writer.writerow(item.model_dump())
            logger.success(f"💾 All data successfully saved to CSV: {filepath}")
        except Exception as e:
            logger.error(f"❌ Error during full CSV export: {e}")

    @staticmethod
    def to_json(data: list[Any], filename: str = "results.json"):
        """Save data to a JSON file"""
        if not data:
            return

        filepath = DATA_DIR / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json_data = [item.model_dump() for item in data]
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            logger.success(f"💾 Data successfully saved to JSON: {filepath}")
        except Exception as e:
            logger.error(f"❌ Error during JSON export: {e}")
