import yaml
from pathlib import Path
from loguru import logger

# 1. ШЛЯХИ ДО ПАПОК (Залишаються в коді, бо це системна частина)
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
AUTH_FILE = DATA_DIR / "auth.json"
CONFIG_PATH = BASE_DIR / "config.yaml"

# 2. АВТОМАТИЧНЕ СТВОРЕННЯ
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --- НОВИЙ БЛОК: ЗАВАНТАЖЕННЯ КОНФІГУРАЦІЇ ---
def load_config():
    if not CONFIG_PATH.exists():
        logger.warning(f"⚠️ Файл {CONFIG_PATH} не знайдено! Використовую дефолтні налаштування.")
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# 3. НАЛАШТУВАННЯ СКРАПІНГУ (Беремо з YAML або ставимо fallback значення)
scraping_cfg = config.get("scraping", {})
BASE_URL = scraping_cfg.get("start_url", "https://quotes.toscrape.com")
MAX_ITEMS = scraping_cfg.get("max_items", 50)
CONCURRENCY = scraping_cfg.get("concurrency", 1)
MAX_RETRIES = 3

# ПАУЗИ
delays_cfg = config.get("delays", {"min": 3, "max": 7})
BASE_DELAY = (delays_cfg["min"], delays_cfg["max"])

# СЕЛЕКТОРИ (для використання в parser.py)
SELECTORS = config.get("selectors", {})

# 4. ТЕХНІЧНІ НАЛАШТУВАННЯ БРАУЗЕРА
browser_cfg = config.get("browser", {})
HEADLESS = browser_cfg.get("headless", False)
TIMEOUT = browser_cfg.get("timeout", 30000)

# Список UA залишаємо тут, бо користувачу зазвичай байдуже на них
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

# 5. КЕРУВАННЯ ПРОКСІ
# Тепер проксі теж можна винести в YAML, але якщо зручно тут — залишаємо
PROXY_LIST = config.get("proxies", [])
USE_PROXY_ROTATION = True if PROXY_LIST else False

PROXY_SETTINGS = PROXY_LIST[0] if PROXY_LIST else None