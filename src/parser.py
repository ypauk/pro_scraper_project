from playwright.async_api import Page
from src.models import QuoteModel
from loguru import logger


class QuoteParser:
    @staticmethod
    async def parse_quotes(page: Page) -> list[QuoteModel]:
        """Знаходить всі цитати на сторінці та перетворює їх у моделі"""
        quotes_data = []
        elements = await page.query_selector_all(".quote")

        for el in elements:
            try:
                text_el = await el.query_selector(".text")
                author_el = await el.query_selector(".author")

                text = await text_el.inner_text() if text_el else ""
                author = await author_el.inner_text() if author_el else ""

                tags_els = await el.query_selector_all(".tag")
                tags = [await t.inner_text() for t in tags_els]

                text = text.replace('“', '').replace('”', '').strip()

                quotes_data.append(QuoteModel(
                    text=text,
                    author=author,
                    tags=tags
                ))
            except Exception as e:
                logger.warning(f"Помилка при парсингу окремої цитати: {e}")

        return quotes_data

    @staticmethod
    async def get_next_page_url(page: Page) -> str | None:
        """
        Шукає посилання на наступну сторінку.
        Якщо кнопки 'Next' немає — повертає None.
        """
        try:
            # Селектор для кнопки Next на quotes.toscrape.com
            next_button = await page.query_selector("li.next a")
            if next_button:
                href = await next_button.get_attribute("href")
                # Перетворюємо відносне посилання (/page/2/) у повне
                base_url = "https://quotes.toscrape.com"
                return f"{base_url}{href}"
            return None
        except Exception as e:
            logger.error(f"Помилка при пошуку наступної сторінки: {e}")
            return None