import yaml
from pathlib import Path
from loguru import logger

# 1. DIRECTORY PATHS
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"  # Logs are stored in a separate root-level directory
CONFIG_PATH = BASE_DIR / "config.yaml"
AUTH_FILE = DATA_DIR / "auth.json"

# 2. AUTO-CREATE REQUIRED DIRECTORIES
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --- CONFIGURATION LOADING ---
def load_config():
    if not CONFIG_PATH.exists():
        logger.warning(
            f"⚠️ Config file {CONFIG_PATH} not found. Using default settings."
        )
        # Default values for book scraping
        return {
            "scraping": {
                "start_url": "https://books.toscrape.com",
                "max_items": 100
            },
            "browser": {
                "headless": True,
                "timeout": 30000
            }
        }

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()

# 3. SCRAPING SETTINGS
scraping_cfg = config.get("scraping", {})
START_URL = scraping_cfg.get("start_url", "https://books.toscrape.com")
MAX_ITEMS = scraping_cfg.get("max_items", 20)
CONCURRENCY = scraping_cfg.get("concurrency", 1)
MAX_RETRIES = 3

# DELAYS
delays_cfg = config.get("delays", {"min": 1, "max": 3})  # Faster delays are acceptable for this site
BASE_DELAY = (delays_cfg["min"], delays_cfg["max"])

# SELECTORS (used in parser.py)
SELECTORS = config.get("selectors", {})

# 4. BROWSER TECHNICAL SETTINGS
browser_cfg = config.get("browser", {})
HEADLESS = browser_cfg.get("headless", True)
TIMEOUT = browser_cfg.get("timeout", 30000)

# User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

# 5. PROXY MANAGEMENT
PROXY_LIST = config.get("proxies", [])
PROXY_SETTINGS = PROXY_LIST[0] if PROXY_LIST else None
