import asyncio
import random
from src.client import BrowserClient
from src.parser import QuoteParser
from src.models import QuoteModel
from loguru import logger
# Додаємо нові утиліти для імітації людини
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

    async def scrape_page(self, semaphore: asyncio.Semaphore, url: str, index: int):
        """
        Обробка сторінки з імітацією реального користувача (скрол, миша, паузи)
        """
        async with semaphore:
            if len(self.results) >= self.max_items:
                return

            # 1. Ротація проксі
            current_proxy = None
            if PROXY_LIST:
                current_proxy = PROXY_LIST[index % len(PROXY_LIST)]
                proxy_label = current_proxy.get('server', 'unknown')
            else:
                proxy_label = "Рідний IP"

            # 2. Унікальний User-Agent
            current_ua = self.client.get_random_ua()

            # 3. Ізольований контекст
            context = await self.client.browser.new_context(
                user_agent=current_ua,
                proxy=current_proxy
            )
            page = await context.new_page()

            try:
                logger.info(f"🧵 [Потік #{index}] Перехід: {url} | Proxy: {proxy_label}")

                # Завантаження сторінки
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                # --- ЕМУЛЯЦІЯ ПОВЕДІНКИ ЛЮДИНИ ---
                # 80% шанс, що користувач поворушить мишкою
                if random.random() < 0.8:
                    await human_mouse_move(page)

                # 60% шанс, що користувач прокрутить сторінку вниз (важливо для Lazy Load)
                if random.random() < 0.6:
                    await smooth_scroll(page)
                    # Після скролу ще трохи рухаємо мишею, ніби читаємо знизу
                    await human_mouse_move(page)
                # --------------------------------

                # Власне парсинг
                new_items = await self.parser.parse_quotes(page)

                async with self._lock:
                    self._update_results(new_items)
                    count = len(self.results)

                logger.success(f"✅ [Потік #{index}] Успішно зібрано. В базі: {count}")

                # Адаптивна пауза після роботи
                min_d = BASE_DELAY[0] * self.concurrency if len(PROXY_LIST) <= 1 else BASE_DELAY[0]
                max_d = BASE_DELAY[1] * self.concurrency if len(PROXY_LIST) <= 1 else BASE_DELAY[1]
                await human_delay(min_d, max_d)

            except Exception as e:
                logger.error(f"❌ [Потік #{index}] Помилка на {url}: {e}")
            finally:
                await context.close()

    async def run(self, urls: list[str]):
        """Запуск паралельної обробки"""
        await self.client.start()
        semaphore = asyncio.Semaphore(self.concurrency)

        try:
            tasks = [self.scrape_page(semaphore, url, i + 1) for i, url in enumerate(urls)]
            await asyncio.gather(*tasks)

            logger.info(f"🏁 Скрапінг завершено. Разом зібрано: {len(self.results)}")
            return self.results
        finally:
            await self.client.stop()

    def _update_results(self, new_items: list[QuoteModel]):
        existing_texts = {item.text for item in self.results}
        for item in new_items:
            if item.text not in existing_texts and len(self.results) < self.max_items:
                self.results.append(item)