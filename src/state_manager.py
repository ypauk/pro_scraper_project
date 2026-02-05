#Цей клас буде відповідати за збереження та читання "контрольної точки".
import json
from pathlib import Path
from loguru import logger

class StateManager:
    def __init__(self, file_path: str = "data/checkpoint.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, url: str, gathered_count: int=0):
        """Зберігає поточний прогрес у файл"""
        state = {
            "last_url": url,
            "count": gathered_count
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=4)
        logger.debug(f"💾 Контрольна точка збережена: {url}")

    def load_checkpoint(self) -> dict | None:
        """Завантажує прогрес, якщо він існує"""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Помилка читання файлу стану: {e}")
        return None

    def clear_checkpoint(self):
        """Видаляє файл стану після успішного завершення"""
        if self.file_path.exists():
            self.file_path.unlink()
            logger.info("🧹 Контрольна точка видалена (роботу завершено).")