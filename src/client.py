import os
import random
from playwright.async_api import async_playwright
# Імпортуємо налаштування
from src.settings import AUTH_FILE, HEADLESS, USER_AGENTS, TIMEOUT, PROXY_SETTINGS
from loguru import logger
from fake_useragent import UserAgent


class BrowserClient:
    def __init__(self, proxy: dict = None):
        self.playwright = None
        self.browser = None
        # Ми прибрали self.context, бо тепер кожен потік у скрапері створює свій контекст
        self.proxy = proxy if proxy else PROXY_SETTINGS

        # Ініціалізуємо генератор випадкових User-Agents
        try:
            self.ua_generator = UserAgent()
        except Exception as e:
            logger.warning(f"⚠️ Не вдалося ініціалізувати fake-useragent: {e}. Буде використано ручний список.")
            self.ua_generator = None

    def get_random_ua(self) -> str:
        """Метод для отримання надійного User-Agent з чітким логуванням джерела"""
        if self.ua_generator:
            try:
                ua = self.ua_generator.random
                logger.info("🌐 Використано динамічний User-Agent (fake-useragent)")
                return ua
            except Exception as e:
                logger.warning(f"📡 Збій мережевої бази User-Agents: {e}")

        # План Б: Випадковий вибір із твого списку в settings.py
        fallback_ua = random.choice(USER_AGENTS)
        logger.info("💾 Використано User-Agent з ручного списку (Fallback)")
        return fallback_ua

    async def start(self):
        """Тільки запуск браузера (без створення зайвих вкладок)"""
        self.playwright = await async_playwright().start()

        # Запуск браузера
        self.browser = await self.playwright.chromium.launch(
            headless=HEADLESS,
            proxy=self.proxy if self.proxy else None
        )

        logger.info(f"🚀 Ядро браузера запущено (Proxy: {'Так' if self.proxy else 'Ні'})")
        # Ми більше не створюємо context і page тут, щоб не було порожніх вікон

    async def stop(self):
        """Повне закриття браузера та ресурсів"""
        try:
            # Закриваємо лише браузер і playwright
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("🛑 Асинхронний клієнт повністю зупинено.")
        except Exception as e:
            logger.error(f"❌ Помилка при зупинці клієнта: {e}")