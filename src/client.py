from playwright.sync_api import sync_playwright
from src.settings import AUTH_FILE, HEADLESS, USER_AGENT, TIMEOUT
from loguru import logger
import os


class BrowserClient:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    def start(self):
        """Запуск браузера з налаштуваннями"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=HEADLESS)

        # Перевіряємо, чи файл існує ТА чи він не порожній
        if AUTH_FILE.exists() and os.path.getsize(AUTH_FILE) > 0:
            storage_state = str(AUTH_FILE)
            logger.info("Завантажуємо збережену сесію з auth.json")
        else:
            storage_state = None
            logger.warning("Файл сесії порожній або відсутній. Працюємо без авторизації.")

        if storage_state:
            logger.info("Завантажуємо збережену сесію з auth.json")
        else:
            logger.warning("Файл сесії не знайдено. Працюємо як гість.")

        # Створюємо контекст (профіль) браузера
        self.context = self.browser.new_context(
            storage_state=storage_state,
            user_agent=USER_AGENT
        )
        self.context.set_default_timeout(TIMEOUT)
        return self.context.new_page()

    def stop(self):
        """Чисте закриття всіх ресурсів"""
        if self.context: self.context.close()
        if self.browser: self.browser.close()
        if self.playwright: self.playwright.stop()
        logger.info("Браузер успішно закрито.")