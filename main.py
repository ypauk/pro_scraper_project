import asyncio
import time
import sys
from loguru import logger
from src.scraper import Scraper
from src.exporter import Exporter
from src.settings import LOG_DIR, PROXY_SETTINGS, CONCURRENCY


async def main():
    # 1. Налаштовуємо логування
    logger.remove()
    logger.add(sys.stdout, level="INFO", colorize=True)
    logger.add(
        LOG_DIR / "debug.log",
        rotation="10 MB",
        retention="10 days",
        level="INFO",
        encoding="utf-8"
    )

    logger.info("🚀 Запуск АВТОНОМНОГО краулера (Варіант В)")

    # 2. Точка входу (лише ОДНЕ посилання)
    start_url = "https://quotes.toscrape.com/"

    # 3. Ініціалізуємо скрапер
    # Примітка: у Варіанті В concurrency використовується всередині scrape_page,
    # але перехід між сторінками йде послідовно через кнопку "Next"
    scraper = Scraper(max_items=50, proxy=PROXY_SETTINGS)

    # --- СТАРТ ТАЙМЕРА ---
    start_time = time.perf_counter()

    # 4. ЗАПУСК КРАУЛЕРА
    # Тепер ми передаємо лише один URL, а не список
    results = await scraper.run(start_url)

    # --- СТОП ТАЙМЕРА ---
    end_time = time.perf_counter()
    total_time = end_time - start_time

    # 5. Експорт та фінальна статистика
    if results:
        # Зберігаємо результат
        file_name = "crawler_quotes.csv"
        Exporter.to_csv(results, file_name)

        logger.success("-" * 40)
        logger.success(f"🏁 Краулінг завершено успішно!")
        logger.info(f"📊 Разом зібрано: {len(results)} цитат")
        logger.info(f"⏱️ Загальний час: {total_time:.2f} сек.")

        # Розрахунок ефективності
        if total_time > 0:
            logger.info(f"⚡ Продуктивність: {len(results) / total_time:.2f} цитат/сек.")
        logger.success("-" * 40)
    else:
        logger.warning("🤔 Дані не знайдено. Перевір селектори або підключення.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Це той самий "Safe Exit", про який я казав —
        # навіть при перериванні можна додати логіку збереження
        logger.warning("\n⏹️ Виконання перервано користувачем.")
    except Exception as e:
        logger.critical(f"💥 Критична помилка: {e}")