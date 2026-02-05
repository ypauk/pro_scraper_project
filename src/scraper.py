import asyncio
import random
from src.client import BrowserClient
from src.parser import QuoteParser
from src.models import QuoteModel
from loguru import logger
from src.utils import human_delay, smooth_scroll, human_mouse_move
from src.settings import BASE_DELAY, CONCURRENCY, PROXY_LIST


class Scraper:
    def __init__(self, max_items: int = 50, proxy: dict = None, concurrency: int = CONCURRENCY):
        self.client = BrowserClient(proxy=proxy)
        self.parser = QuoteParser()
        self.max_items = max_items
        self.concurrency = concurrency
        self.results: list[QuoteModel] = []
        self._lock = asyncio.Lock()

    async def scrape_page(self, url: str, index: int) -> str | None:
        """
        Обробляє сторінку та ПОВЕРТАЄ URL наступної сторінки, якщо він є.
        """
        if len(self.results) >= self.max_items:
            return None

        # 1. Вибір проксі та UA
        current_proxy = PROXY_LIST[index % len(PROXY_LIST)] if PROXY_LIST else None
        current_ua = self.client.get_random_ua()

        context = await self.client.browser.new_context(
            user_agent=current_ua,
            proxy=current_proxy
        )
        page = await context.new_page()
        next_page_url = None

        try:
            logger.info(f"🚀 [Сторінка #{index}] Перехід: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # --- ЕМУЛЯЦІЯ ---
            if random.random() < 0.8: await human_mouse_move(page)
            if random.random() < 0.6:
                await smooth_scroll(page)
                await human_mouse_move(page)

            # --- ПАРСИНГ ДАНИХ ---
            new_items = await self.parser.parse_quotes(page)

            # --- ПОШУК НАСТУПНОЇ СТОРІНКИ (Варіант В) ---
            next_page_url = await self.parser.get_next_page_url(page)

            async with self._lock:
                self._update_results(new_items)
                count = len(self.results)

            logger.success(f"✅ [Сторінка #{index}] Зібрано {len(new_items)} шт. (Разом: {count})")

            await human_delay(BASE_DELAY[0], BASE_DELAY[1])

        except Exception as e:
            logger.error(f"❌ Помилка на сторінці #{index}: {e}")
        finally:
            await context.close()
            return next_page_url

    async def run(self, start_url: str):
        """
        Точка входу для Crawler. Йде по кнопках 'Next'.
        """
        await self.client.start()
        current_url = start_url
        page_index = 1

        try:
            # Працюємо, поки є посилання і ми не набрали ліміт
            while current_url and len(self.results) < self.max_items:
                # Викликаємо обробку і отримуємо посилання на майбутню сторінку
                current_url = await self.scrape_page(current_url, page_index)
                page_index += 1

                if not current_url:
                    logger.info("🏁 Кнопка 'Next' не знайдена або ліміт досягнуто. Зупиняюсь.")

            logger.info(f"🏁 Краулінг завершено. Всього зібрано: {len(self.results)}")
            return self.results
        finally:
            await self.client.stop()

    def _update_results(self, new_items: list[QuoteModel]):
        existing_texts = {item.text for item in self.results}
        for item in new_items:
            if item.text not in existing_texts and len(self.results) < self.max_items:
                self.results.append(item)