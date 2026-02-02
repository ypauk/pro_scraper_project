from pathlib import Path

# Шляхи до папок
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
AUTH_FILE = BASE_DIR / "auth.json"

# Налаштування скрапінгу
BASE_URL = "https://quotes.toscrape.com"
LOGIN_URL = f"{BASE_URL}/login"

# Налаштування браузера
HEADLESS = False  # Постав True для роботи у фоні
TIMEOUT = 30000   # 30 секунд
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# Створюємо папку data, якщо її немає
DATA_DIR.mkdir(exist_ok=True)