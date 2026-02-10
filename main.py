import asyncio
import time
import sys
from loguru import logger
from src.scraper import Scraper
from src.exporter import Exporter
from src.settings import LOG_DIR, PROXY_SETTINGS, START_URL, MAX_ITEMS


async def main():
    # 1. Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )
    logger.add(
        LOG_DIR / "books_scraper.log",
        rotation="10 MB",
        retention="5 days",
        level="INFO",
        encoding="utf-8"
    )

    logger.info("🚀 Launching universal scraper for books.toscrape.com")

    # 2. Entry point and limits (from settings)
    start_url = START_URL
    max_books = MAX_ITEMS

    # 3. Initialize scraper
    # Passing proxy and max item limit
    scraper = Scraper(max_items=max_books, proxy=PROXY_SETTINGS)

    # --- START TIMER ---
    start_time = time.perf_counter()

    # 4. Run the crawler
    # The run method sequentially navigates pages via "Next" until max_items is reached
    results = await scraper.run(start_url)

    # --- STOP TIMER ---
    end_time = time.perf_counter()
    total_time = end_time - start_time

    # 5. Export results and final statistics
    if results:
        # Save results to data folder
        output_file = "live_results.csv"
        Exporter.to_csv(results, output_file)

        logger.success("-" * 45)
        logger.success("🏁 Scraping completed successfully!")
        logger.info(f"📚 Total books collected: {len(results)}")
        logger.info(f"⏱️ Total runtime: {total_time:.2f} sec.")

        # Calculate efficiency
        if total_time > 0:
            avg_speed = len(results) / total_time
            logger.info(f"⚡ Collection speed: {avg_speed:.2f} books/sec")

        logger.info(f"📂 Data saved to: {output_file}")
        logger.success("-" * 45)
    else:
        logger.warning("🤔 No data found. Possible reasons: selector changes or site blocking.")


if __name__ == "__main__":
    try:
        # Run the async event loop
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\n⏹️ Process stopped by user (Ctrl+C).")
    except Exception as e:
        logger.critical(f"💥 Critical error during execution: {e}")
