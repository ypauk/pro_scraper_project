from src.scraper import Scraper
from src.exporter import Exporter
from loguru import logger
from src.settings import DATA_DIR


def main():
    # Налаштовуємо запис у файл. Логи старіші за 10 днів будуть видалятися.
    logger.add(DATA_DIR / "debug.log", rotation="10 MB", retention="10 days", level="INFO")

    logger.info("Запуск проекту: Professional Quote Scraper")

    # 1. Ініціалізуємо скрапер (задаємо ліміт, наприклад, 35 цитат)
    scraper = Scraper(max_items=35)

    # 2. Запускаємо процес збору
    results = scraper.run()

    # 3. Якщо дані зібрані — експортуємо їх
    if results:
        logger.info(f"Збір завершено. Починаємо експорт {len(results)} елементів...")

        # Зберігаємо в обидва формати для прикладу
        Exporter.to_csv(results, "final_quotes.csv")
        Exporter.to_json(results, "final_quotes.json")

        logger.success("Проект виконано успішно!")
    else:
        logger.error("Дані не були зібрані. Перевірте підключення або селектори.")


if __name__ == "__main__":
    main()