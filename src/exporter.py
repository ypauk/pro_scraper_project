import csv
import json
from src.models import QuoteModel
from src.settings import DATA_DIR
from loguru import logger


class Exporter:
    @staticmethod
    def to_csv(data: list[QuoteModel], filename: str = "quotes.csv"):
        filepath = DATA_DIR / filename
        if not data:
            logger.warning("Немає даних для експорту.")
            return

        # Перетворюємо моделі Pydantic у словники
        fieldnames = data[0].model_dump().keys()

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item.model_dump())

        logger.info(f"Дані збережено в CSV: {filepath}")

    @staticmethod
    def to_json(data: list[QuoteModel], filename: str = "quotes.json"):
        filepath = DATA_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            # Сериалізуємо список моделей
            json_data = [item.model_dump() for item in data]
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        logger.info(f"Дані збережено в JSON: {filepath}")