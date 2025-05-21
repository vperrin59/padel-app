from dotenv import load_dotenv
import os

load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://urbanpadellausanne.matchpoint.com.es"
CHECK_INTERVAL_MINUTES = 5
NOTIFICATION_METHOD = "telegram"

MY_LEVEL = 2.13

MIN_PARTNER_LEVEL = 1.5

urban_link_prefix = f"https://urbanpadellausanne.matchpoint.com.es/Matches/"