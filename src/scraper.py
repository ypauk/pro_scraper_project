import asyncio
import random
from src.client import BrowserClient
from src.parser import QuoteParser
from src.models import QuoteModel
from loguru import logger
from src.utils import human_delay, smooth_scroll, human_mouse_move
from src.settings import BASE_DELAY, CONCURRENCY, PROXY_LIST
from src.state_manager import StateManager
from src.exporter import Exporter


class Scraper:
    def __init__(self, max_items: int = 50, proxy: dict = None, concurrency: int = CONCURRENCY):
        self.client = BrowserClient(proxy=proxy)
        self.parser = QuoteParser()
        self.max_items = max_items
        self.concurrency = concurrency
        self.results: list[QuoteModel] = []
        self._lock = asyncio.Lock()
        self.state_manager = StateManager()

    async def scrape_page(self, url: str, index: int) -> str | None:
        if len(self.results) >= self.max_items:
            return None

        current_proxy = PROXY_LIST[index % len(PROXY_LIST)] if PROXY_LIST else None
        current_ua = self.client.get_random_ua()

        context = await self.client.browser.new_context(
            user_agent=current_ua,
            proxy=current_proxy
        )
        page = await context.new_page()

        try:
            # Тут ми впевнені, що url - це рядок
            logger.info(f"🚀 [Сторінка #{index}] Перехід: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            if random.random() < 0.8: await human_mouse_move(page)
            if random.random() < 0.6:
                await smooth_scroll(page)
                await human_mouse_move(page)

            new_items = await self.parser.parse_quotes(page)
            next_page_url = await self.parser.get_next_page_url(page)

            async with self._lock:
                self._update_results(new_items)
                count = len(self.results)

            logger.success(f"✅ [Сторінка #{index}] Зібрано {len(new_items)} шт. (Разом: {count})")

            if next_page_url:
                self.state_manager.save_checkpoint(next_page_url)

            await human_delay(BASE_DELAY[0], BASE_DELAY[1])
            return next_page_url

        except Exception as e:
            logger.error(f"❌ Помилка на сторінці #{index}: {e}")
            return "ERROR_SIGNAL"
        finally:
            await context.close()

    async def run(self, start_url: str):
        await self.client.start()

        # --- ВИПРАВЛЕНИЙ БЛОК ЗАВАНТАЖЕННЯ ---
        checkpoint_data = self.state_manager.load_checkpoint()

        # Перевіряємо структуру завантажених даних
        if isinstance(checkpoint_data, dict):
            current_url = checkpoint_data.get("last_url", start_url)
        elif isinstance(checkpoint_data, str):
            current_url = checkpoint_data
        else:
            current_url = start_url

        if current_url != start_url:
            logger.info(f"♻️ Відновлення з чекпоїнта: {current_url}")
        # ---------------------------------------

        page_index = 1

        try:
            while current_url and len(self.results) < self.max_items:
                # Передаємо в scrape_page вже гарантовано чистий URL (рядок)
                result = await self.scrape_page(current_url, page_index)

                if result == "ERROR_SIGNAL":
                    logger.warning(f"⚠️ Переривання через збій. Чекпоїнт залишився на: {current_url}")
                    break

                current_url = result
                page_index += 1

            if current_url is None and len(self.results) < self.max_items:
                logger.info("🏁 Сайт закінчився.")
                self.state_manager.clear_checkpoint()
            elif len(self.results) >= self.max_items:
                logger.info(f"🎯 Ліміт у {self.max_items} досягнуто.")
                self.state_manager.clear_checkpoint()

            return self.results

        except Exception as e:
            logger.critical(f"💥 Критичний збій: {e}")
            return self.results
        finally:
            await self.client.stop()

    def _update_results(self, new_items: list[QuoteModel]):
        existing_texts = {item.text for item in self.results}
        for item in new_items:
            if item.text not in existing_texts and len(self.results) < self.max_items:
                self.results.append(item)
                Exporter.append_to_csv(item, filename="live_results.csv")