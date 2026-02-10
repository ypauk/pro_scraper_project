import os
import random
from playwright.async_api import async_playwright
# Import settings
from src.settings import AUTH_FILE, HEADLESS, USER_AGENTS, TIMEOUT, PROXY_LIST
from loguru import logger
from fake_useragent import UserAgent


class BrowserClient:
    def __init__(self, proxy: dict = None):
        self.playwright = None
        self.browser = None
        # We removed self.context because now each scraper worker creates its own context
        self.proxy = proxy or (PROXY_LIST[0] if PROXY_LIST else None)

        # Initialize random User-Agent generator
        try:
            self.ua_generator = UserAgent()
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to initialize fake-useragent: {e}. Falling back to manual list."
            )
            self.ua_generator = None

    def get_random_ua(self) -> str:
        """Return a reliable User-Agent with clear logging of the source"""
        if self.ua_generator:
            try:
                ua = self.ua_generator.random
                logger.info("🌐 Using dynamic User-Agent (fake-useragent)")
                return ua
            except Exception as e:
                logger.warning(f"📡 User-Agent network database error: {e}")

        # Plan B: Random choice from manual list in settings.py
        fallback_ua = random.choice(USER_AGENTS)
        logger.info("💾 Using User-Agent from manual list (fallback)")
        return fallback_ua

    async def start(self):
        """Start browser only (without creating extra tabs or contexts)"""
        self.playwright = await async_playwright().start()

        # Launch browser
        self.browser = await self.playwright.chromium.launch(
            headless=HEADLESS,
            proxy=self.proxy if self.proxy else None
        )

        logger.info(
            f"🚀 Browser engine started (Proxy: {'Enabled' if self.proxy else 'Disabled'})"
        )
        # We no longer create context and page here to avoid empty windows

    async def stop(self):
        """Fully close browser and release resources"""
        try:
            # Close browser and playwright only
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("🛑 Asynchronous browser client stopped successfully.")
        except Exception as e:
            logger.error(f"❌ Error while stopping browser client: {e}")
