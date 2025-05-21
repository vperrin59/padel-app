import requests
from models import Match
from config import *

def send_notification(match: Match):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": str(match),
    }
    requests.get(url, params=params)

if __name__ == "__main__":
    if False:
        url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/getUpdates"
        resp = requests.get(url)
        print(resp.json())
    else:
        MESSAGE = "🚨 New match found at 20:00 on Court 1!"
        url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": MESSAGE
        }
        requests.get(url, params=params)