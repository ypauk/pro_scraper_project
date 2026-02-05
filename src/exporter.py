import csv
import json
from src.models import QuoteModel
from src.settings import DATA_DIR
from loguru import logger


class Exporter:
    @staticmethod
    def append_to_csv(item: QuoteModel, filename: str = "quotes.csv"):
        """Додає один запис у CSV файл (режим дозапису)"""
        filepath = DATA_DIR / filename
        file_exists = filepath.exists()

        # Отримуємо дані у вигляді словника
        row = item.model_dump()
        fieldnames = row.keys()

        try:
            with open(filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                # Якщо файл новий — записуємо заголовок
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
        except Exception as e:
            logger.error(f"Помилка при записі в CSV: {e}")

    @staticmethod
    def to_csv(data: list[QuoteModel], filename: str = "quotes.csv"):
        """Класичний метод для збереження всього списку відразу"""
        filepath = DATA_DIR / filename
        if not data:
            return

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
            json_data = [item.model_dump() for item in data]
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        logger.info(f"Дані збережено в JSON: {filepath}")