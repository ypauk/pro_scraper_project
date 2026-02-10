import asyncio
import random
from src.client import BrowserClient
from src.parser import BookParser  # Using the BookParser for books
from src.models import BookModel  # Using BookModel for typed results
from loguru import logger
from src.utils import human_delay, smooth_scroll, human_mouse_move
from src.settings import BASE_DELAY, CONCURRENCY, PROXY_LIST
from src.state_manager import StateManager
from src.exporter import Exporter


class Scraper:
    def __init__(self, max_items: int = 50, proxy: dict = None, concurrency: int = CONCURRENCY):
        # Initialize browser client with optional proxy
        self.client = BrowserClient(proxy=proxy)
        # Initialize book parser
        self.parser = BookParser()
        self.max_items = max_items
        self.concurrency = concurrency
        self.results: list[BookModel] = []  # Store all scraped books
        self._lock = asyncio.Lock()  # Async lock for thread-safe updates
        self.state_manager = StateManager()  # Checkpoint manager to resume scraping

    async def scrape_page(self, url: str, index: int) -> str | None:
        """Process a single catalog page of books."""
        if len(self.results) >= self.max_items:
            return None

        # Rotate proxy if available
        current_proxy = PROXY_LIST[index % len(PROXY_LIST)] if PROXY_LIST else None
        # Pick a random User-Agent for realistic behavior
        current_ua = self.client.get_random_ua()

        # Create new browser context for this page
        context = await self.client.browser.new_context(
            user_agent=current_ua,
            proxy=current_proxy
        )
        page = await context.new_page()

        try:
            logger.info(f"📖 [Page #{index}] Loading: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Human-like behavior simulation
            if random.random() < 0.7:
                await human_mouse_move(page)
            if random.random() < 0.5:
                await smooth_scroll(page)

            # Parse books using BookParser
            new_items = await self.parser.parse_books(page)
            next_page_url = await self.parser.get_next_page_url(page)

            # Safely update results
            async with self._lock:
                self._update_results(new_items)
                count = len(self.results)

            logger.success(f"✔️ [Page #{index}] Processed {len(new_items)} books (Total: {count})")

            # Save checkpoint to resume later if needed
            if next_page_url:
                self.state_manager.save_checkpoint(next_page_url)

            # Delay between pages for human-like crawling
            await human_delay(BASE_DELAY[0], BASE_DELAY[1])
            return next_page_url

        except Exception as e:
            logger.error(f"❌ Error on page #{index}: {e}")
            return "ERROR_SIGNAL"
        finally:
            await context.close()

    async def run(self, start_url: str):
        """Main crawler loop."""
        await self.client.start()

        # Restore from checkpoint if exists
        checkpoint_data = self.state_manager.load_checkpoint()
        if isinstance(checkpoint_data, dict):
            current_url = checkpoint_data.get("last_url", start_url)
        elif isinstance(checkpoint_data, str):
            current_url = checkpoint_data
        else:
            current_url = start_url

        if current_url != start_url:
            logger.info(f"♻️ Resuming session from: {current_url}")

        page_index = 1

        try:
            while current_url and len(self.results) < self.max_items:
                result = await self.scrape_page(current_url, page_index)

                if result == "ERROR_SIGNAL":
                    logger.warning(f"⚠️ Scraping paused due to error. Stopped at: {current_url}")
                    break

                current_url = result
                page_index += 1

            # Finalization
            if current_url is None:
                logger.info("🏁 All catalog pages processed.")
                self.state_manager.clear_checkpoint()
            elif len(self.results) >= self.max_items:
                logger.info(f"🎯 Max limit of {self.max_items} items reached.")
                self.state_manager.clear_checkpoint()

            return self.results

        except Exception as e:
            logger.critical(f"💥 Critical engine error: {e}")
            return self.results
        finally:
            await self.client.stop()

    def _update_results(self, new_items: list[BookModel]):
        """Add only unique books and write them to CSV on the fly."""
        # Use product_url as a unique identifier
        existing_urls = {item.product_url for item in self.results}

        for item in new_items:
            if item.product_url not in existing_urls and len(self.results) < self.max_items:
                self.results.append(item)
                # Append to CSV in real-time (data/live_results.csv)
                Exporter.append_to_csv(item, filename="live_results.csv")
