from playwright.async_api import Page
from src.models import BookModel
from loguru import logger
from urllib.parse import urljoin
# Import SELECTORS and START_URL from your settings
from src.settings import SELECTORS, START_URL


class BookParser:
    @staticmethod
    async def parse_books(page: Page) -> list[BookModel]:
        """Extract all books from the page using selectors defined in config.yaml"""
        books_data = []

        # Main book container selector (article.product_pod)
        book_selector = SELECTORS.get("book_card", "article.product_pod")
        elements = await page.query_selector_all(book_selector)

        for el in elements:
            try:
                # Get selectors from config
                title_sel = SELECTORS.get("title", "h3 a")
                price_sel = SELECTORS.get("price", "p.price_color")
                avail_sel = SELECTORS.get("availability", ".instock.availability")
                rating_sel = SELECTORS.get("rating", "p.star-rating")
                image_sel = SELECTORS.get("image", "div.image_container img")

                # Extract elements
                title_el = await el.query_selector(title_sel)
                price_el = await el.query_selector(price_sel)
                avail_el = await el.query_selector(avail_sel)
                rating_el = await el.query_selector(rating_sel)
                image_el = await el.query_selector(image_sel)

                # Data extraction
                # Title is often truncated in text, so we use the 'title' attribute
                title = await title_el.get_attribute("title") if title_el else "Unknown"

                # Product link
                link_relative = await title_el.get_attribute("href") if title_el else ""
                product_url = urljoin(page.url, link_relative)

                price = await price_el.inner_text() if price_el else "0"
                availability = await avail_el.inner_text() if avail_el else "Unknown"

                # Rating is stored in CSS class name (e.g. "star-rating Three")
                rating_class = await rating_el.get_attribute("class") if rating_el else ""

                # Image: extract src and convert to absolute URL
                img_relative = await image_el.get_attribute("src") if image_el else ""
                image_url = urljoin(page.url, img_relative)

                # Create model instance (BookModel validators will clean price and rating)
                books_data.append(BookModel(
                    title=title,
                    price=price,
                    availability=availability,
                    rating=rating_class,
                    image_url=image_url,
                    product_url=product_url
                ))
            except Exception as e:
                logger.warning(f"Error while parsing a single book item: {e}")

        return books_data

    @staticmethod
    async def get_next_page_url(page: Page) -> str | None:
        """Find and return the next page URL using the next_button selector"""
        try:
            next_selector = SELECTORS.get("next_button", "li.next a")
            next_button = await page.query_selector(next_selector)

            if next_button:
                href = await next_button.get_attribute("href")
                if href:
                    # Use urljoin to properly resolve relative URLs
                    return urljoin(page.url, href)
            return None
        except Exception as e:
            logger.error(f"Error while locating the next page: {e}")
            return None
