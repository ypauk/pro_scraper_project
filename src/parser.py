from playwright.sync_api import Page
from src.models import QuoteModel


class QuoteParser:
    @staticmethod
    def parse_quotes(page: Page) -> list[QuoteModel]:
        """Знаходить всі цитати на сторінці та перетворює їх у моделі"""
        quotes_data = []

        # Шукаємо всі блоки цитат
        elements = page.query_selector_all(".quote")

        for el in elements:
            # Витягуємо текст
            text = el.query_selector(".text").inner_text()
            # Витягуємо автора
            author = el.query_selector(".author").inner_text()
            # Витягуємо теги (якщо є)
            tags_els = el.query_selector_all(".tag")
            tags = [t.inner_text() for t in tags_els]

            # Створюємо об'єкт моделі (тут спрацює валідація!)
            quote_obj = QuoteModel(
                text=text,
                author=author,
                tags=tags
            )
            quotes_data.append(quote_obj)

        return quotes_data