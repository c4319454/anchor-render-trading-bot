from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from datetime import datetime

from broker_test import test_forex_login

app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

PENDING_SIGNALS = []

@app.get("/")
def home():
    return {
        "status": "Anchor Bot Online",
        "mode": "signal hub",
        "time": datetime.utcnow().isoformat()
    }

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"ok": False, "error": "Invalid JSON"}

    action = str(data.get("action", "")).lower()
    symbol = data.get("symbol", "EUR/USD")
    secret = data.get("secret", "")

    if WEBHOOK_SECRET and secret != WEBHOOK_SECRET:
        return {"ok": False, "error": "bad secret"}

    if action not in ["buy", "sell"]:
        return {"ok": False, "error": "invalid action"}

    signal = {
        "id": len(PENDING_SIGNALS) + 1,
        "action": action,
        "symbol": symbol,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }

    PENDING_SIGNALS.append(signal)

    return {
        "ok": True,
        "message": "Signal received and queued",
        "signal": signal
    }

@app.get("/signals/next")
def get_next_signal():
    for signal in PENDING_SIGNALS:
        if signal["status"] == "pending":
            return {
                "ok": True,
                "signal": signal
            }

    return {
        "ok": True,
        "signal": None
    }

@app.post("/signals/{signal_id}/done")
def mark_signal_done(signal_id: int):
    for signal in PENDING_SIGNALS:
        if signal["id"] == signal_id:
            signal["status"] = "done"
            signal["completed_at"] = datetime.utcnow().isoformat()
            return {
                "ok": True,
                "signal": signal
            }

    return {
        "ok": False,
        "error": "Signal not found"
    }

@app.get("/signals")
def list_signals():
    return {
        "ok": True,
        "signals": PENDING_SIGNALS
    }

@app.get("/broker-test")
async def broker_test():
    result = await test_forex_login()
    return JSONResponse(result)
