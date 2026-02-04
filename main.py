import asyncio
import time  # Додаємо для вимірювання часу
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

    logger.info("🚀 Запуск УНІВЕРСАЛЬНОГО асинхронного скрапера")

    # 2. Готуємо список URL (перші 5 сторінок)
    urls_to_scrape = [f"https://quotes.toscrape.com/page/{i}/" for i in range(1, 6)]

    # 3. Ініціалізуємо скрапер
    # Використовуємо CONCURRENCY з settings, якщо хочеш керувати через файл налаштувань
    scraper = Scraper(max_items=100, concurrency=CONCURRENCY, proxy=PROXY_SETTINGS)

    # --- СТАРТ ТАЙМЕРА ---
    start_time = time.perf_counter()

    # 4. ВЛАСНЕ ЗАПУСК
    results = await scraper.run(urls_to_scrape)

    # --- СТОП ТАЙМЕРА ---
    end_time = time.perf_counter()
    total_time = end_time - start_time

    # 5. Експорт та фінальна статистика
    if results:
        Exporter.to_csv(results, "parallel_quotes.csv")

        # Виводимо красивий звіт
        logger.success("-" * 40)
        logger.success(f"🏁 Скрапінг завершено успішно!")
        logger.info(f"📊 Зібрано цитат: {len(results)}")
        logger.info(f"⏱️ Загальний час: {total_time:.2f} сек.")

        # Рахуємо середню швидкість на одну сторінку (не на цитату, бо ми скрейпимо сторінками)
        pages_count = len(urls_to_scrape)
        speed_per_page = total_time / pages_count
        logger.info(f"⚡ Середня швидкість: {speed_per_page:.2f} сек./сторінка")
        logger.success("-" * 40)
    else:
        logger.warning("🤔 Жодних даних не зібрано.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\n⏹️ Виконання перервано користувачем.")
    except Exception as e:
        logger.critical(f"💥 Критична помилка: {e}")