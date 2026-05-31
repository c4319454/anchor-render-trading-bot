from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import requests
from datetime import datetime

from broker_test import test_forex_login

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text
            },
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", str(e))

@app.get("/")
def home():
    return {
        "status": "Anchor Bot Online",
        "time": datetime.utcnow().isoformat()
    }

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    action = str(data.get("action", "")).lower()
    secret = data.get("secret", "")

    if WEBHOOK_SECRET and secret != WEBHOOK_SECRET:
        return {"ok": False, "error": "bad secret"}

    if action not in ["buy", "sell"]:
        return {"ok": False, "error": "invalid action"}

    send_telegram_message(
        f"⚓ Anchor Signal\nAction: {action.upper()}"
    )

    return {
        "ok": True,
        "action": action
    }

@app.get("/broker-test")
async def broker_test():
    result = await test_forex_login()
    return JSONResponse(result)
