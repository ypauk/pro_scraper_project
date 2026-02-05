from pathlib import Path

# 1. ШЛЯХИ ДО ПАПОК
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
AUTH_FILE = DATA_DIR / "auth.json"

# 2. АВТОМАТИЧНЕ СТВОРЕННЯ
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 3. НАЛАШТУВАННЯ СКРАПІНГУ
BASE_URL = "https://quotes.toscrape.com"
LOGIN_URL = f"{BASE_URL}/login"
MAX_RETRIES = 3

# --- НОВИЙ БЛОК: ПОТОКИ ТА ПАУЗИ ---
CONCURRENCY = 1          # Кількість одночасних вкладок
# Базова пауза для одного віртуального користувача (в секундах)
BASE_DELAY = (3, 7)
# ----------------------------------

# 4. ТЕХНІЧНІ НАЛАШТУВАННЯ БРАУЗЕРА
HEADLESS = False
TIMEOUT = 30000

# Список для "плану Б" (fallback)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edge/120.0.0.0"
]

# 5. КЕРУВАННЯ ПРОКСІ
# Тепер це список [ ], як того очікує scraper.py
PROXY_LIST = [
    #{"server": "http://118.193.37.241:3129", "username": "user1", "password": "pass1"},
    #{"server": "http://217.217.254.94:80"},
    # {"server": "http://45.56.78.12:8080"}, # Можна додавати нові
]

# Флаг для увімкнення ротації
#Кожен потік (вкладка), який відкриває скрапер, отримує свою унікальну адресу зі списку PROXY_LIST. Потік
#1 йде через Німеччину, Потік #2 — через Сінгапур і так далі.
USE_PROXY_ROTATION = True



# Якщо хочеш ПОВНІСТЮ вимкнути проксі для тестів, розкоментуй рядок нижче:
# PROXY_LIST = []

# Для сумісності зі старим кодом (не обов'язково, але корисно)
PROXY_SETTINGS = PROXY_LIST[0] if PROXY_LIST else None