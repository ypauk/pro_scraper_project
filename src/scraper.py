from src.client import BrowserClient
from src.parser import QuoteParser
from src.models import QuoteModel
from loguru import logger
from src.utils import human_delay


class Scraper:
    def __init__(self, max_items: int = 50):
        self.client = BrowserClient()
        self.parser = QuoteParser()
        self.max_items = max_items
        self.results: list[QuoteModel] = []

    def run(self):
        """Основний цикл роботи скрапера"""
        page = self.client.start()

        try:
            page.goto("https://quotes.toscrape.com/scroll")
            logger.info("Починаємо збір даних зі скролом...")

            while len(self.results) < self.max_items:
                # 1. Парсимо те, що вже завантажилось
                new_items = self.parser.parse_quotes(page)

                # 2. Оновлюємо список результатів (унікальними цитатами)
                self._update_results(new_items)
                logger.info(f"Прогрес: {len(self.results)} / {self.max_items}")

                if len(self.results) >= self.max_items:
                    break

                # 3. Скролимо вниз для підвантаження нових даних
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                # 4. Чекаємо на підвантаження (динамічна пауза)
                human_delay(2,4)

            logger.success(f"Збір завершено! Зібрано {len(self.results)} цитат.")
            return self.results

        except Exception as e:
            logger.error(f"Помилка під час скрапінгу: {e}")
        finally:
            self.client.stop()

    def _update_results(self, new_items: list[QuoteModel]):
        """Додає тільки ті цитати, яких ще немає в списку"""
        existing_texts = {item.text for item in self.results}
        for item in new_items:
            if item.text not in existing_texts and len(self.results) < self.max_items:
                self.results.append(item)