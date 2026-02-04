from playwright.async_api import Page  # Змінено на async_api
from src.models import QuoteModel
from loguru import logger


class QuoteParser:
    @staticmethod
    async def parse_quotes(page: Page) -> list[QuoteModel]:  # Додано async
        """Знаходить всі цитати на сторінці та перетворює їх у моделі (Асинхронно)"""
        quotes_data = []

        # Шукаємо всі блоки цитат (додано await)
        elements = await page.query_selector_all(".quote")

        for el in elements:
            try:
                # Кожен запит до елемента тепер теж асинхронний
                text_el = await el.query_selector(".text")
                author_el = await el.query_selector(".author")

                # Отримуємо текст через await
                text = await text_el.inner_text() if text_el else ""
                author = await author_el.inner_text() if author_el else ""

                # Витягуємо теги
                tags_els = await el.query_selector_all(".tag")
                tags = []
                for t in tags_els:
                    tags.append(await t.inner_text())

                # Очищення тексту (прибираємо типографські лапки)
                text = text.replace('“', '').replace('”', '').strip()

                # Створюємо об'єкт моделі
                quote_obj = QuoteModel(
                    text=text,
                    author=author,
                    tags=tags
                )
                quotes_data.append(quote_obj)

            except Exception as e:
                logger.warning(f"Помилка при парсингу окремої цитати: {e}")

        return quotes_data