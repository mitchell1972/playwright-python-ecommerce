import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://demo.saleor.io")
BROWSER = os.getenv("BROWSER", "chromium")
HEADLESS = os.getenv("HEADLESS", "True").lower() == 'true'
TIMEOUT = int(os.getenv("TIMEOUT", "10000"))
