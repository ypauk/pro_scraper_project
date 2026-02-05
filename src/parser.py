from playwright.async_api import Page
from src.models import QuoteModel
from loguru import logger
# Ми вже імпортували SELECTORS та BASE_URL раніше у settings
from src.settings import SELECTORS, BASE_URL


class QuoteParser:
    @staticmethod
    async def parse_quotes(page: Page) -> list[QuoteModel]:
        """Знаходить всі цитати на сторінці, використовуючи гнучкі селектори з конфігу"""
        quotes_data = []

        # Беремо селектор головного блоку з конфігу (дефолт: .quote)
        quote_selector = SELECTORS.get("quote_block", ".quote")
        elements = await page.query_selector_all(quote_selector)

        for el in elements:
            try:
                # Беремо селектори полів
                text_selector = SELECTORS.get("text", ".text")
                author_selector = SELECTORS.get("author", ".author")
                tag_selector = SELECTORS.get("tags", ".tag")

                text_el = await el.query_selector(text_selector)
                author_el = await el.query_selector(author_selector)

                text = await text_el.inner_text() if text_el else ""
                author = await author_el.inner_text() if author_el else ""

                tags_els = await el.query_selector_all(tag_selector)
                tags = [await t.inner_text() for t in tags_els]

                # Очищення тексту
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
        """Шукає посилання на наступну сторінку за гнучким селектором"""
        try:
            # Селектор кнопки Next з конфігу (дефолт: li.next a)
            next_selector = SELECTORS.get("next_button", "li.next a")
            next_button = await page.query_selector(next_selector)

            if next_button:
                href = await next_button.get_attribute("href")
                if href:
                    # Якщо посилання відносне (/page/2/), додаємо базовий домен
                    if href.startswith("/"):
                        return f"{BASE_URL.rstrip('/')}{href}"
                    return href
            return None
        except Exception as e:
            logger.error(f"Помилка при пошуку наступної сторінки: {e}")
            return None