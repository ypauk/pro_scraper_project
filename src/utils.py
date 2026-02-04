import random
import asyncio
from loguru import logger


async def human_delay(min_sec=1, max_sec=3):
    """Асинхронно імітує роздуми людини."""
    sleep_time = random.uniform(min_sec, max_sec)
    await asyncio.sleep(sleep_time)


async def smooth_scroll(page):
    """
    Плавний скрол з ефектом 'перечитування' (іноді повертається трохи вгору).
    """
    try:
        total_height = await page.evaluate("document.body.scrollHeight")
        current_scroll = 0

        logger.debug("📜 Починаю реалістичний скрол...")

        while current_scroll < total_height:
            # Визначаємо крок (вниз)
            step = random.randint(400, 800)
            current_scroll += step
            await page.mouse.wheel(0, step)
            await asyncio.sleep(random.uniform(0.4, 0.9))

            # --- ЕФЕКТ ПЕРЕЧИТУВАННЯ ---
            # З імовірністю 15% людина "повертається" трохи назад
            if random.random() < 0.15 and current_scroll > 1000:
                back_step = random.randint(-400, -200)
                current_scroll += back_step
                await page.mouse.wheel(0, back_step)
                logger.debug("👀 Повернувся трохи вгору (ефект перечитування)")
                await asyncio.sleep(random.uniform(1.0, 2.0))  # Пауза на "читання"

            # Оновлюємо висоту
            total_height = await page.evaluate("document.body.scrollHeight")

            if current_scroll > 15000:  # Захист від нескінченних сторінок
                break

    except Exception as e:
        logger.error(f"⚠️ Помилка скролу: {e}")


async def human_mouse_move(page):
    """Емуляція складних рухів миші з різною швидкістю."""
    try:
        viewport = page.viewport_size or {'width': 1280, 'height': 720}

        for _ in range(random.randint(2, 4)):
            x = random.randint(50, viewport['width'] - 50)
            y = random.randint(50, viewport['height'] - 50)

            # steps=30-60 робить рух дуже повільним і тремтливим
            await page.mouse.move(x, y, steps=random.randint(30, 60))
            await asyncio.sleep(random.uniform(0.2, 0.6))

    except Exception as e:
        logger.debug(f"Миша не активна: {e}")