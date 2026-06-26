import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_signal(symbol: str, signal: dict):
    direction_emoji = "🟢" if signal["direction"] == "BUY" else "🔴"
    reasons_text = "\n".join(f"• {r}" for r in signal["reasons"])

    text = (
        f"{direction_emoji} *{signal['direction']} SIGNAL*\n\n"
        f"💱 Juftlik: `{symbol}`\n"
        f"🎯 Entry: `{signal['entry']}`\n"
        f"🛑 SL: `{signal['sl']}`\n"
        f"✅ TP: `{signal['tp']}`\n"
        f"⚖️ Risk/Reward: 1:{signal['risk_reward']}\n\n"
        f"📊 Tahlil (SMC):\n{reasons_text}\n\n"
        f"⚠️ Bu avtomatik signal, moliyaviy maslahat emas. Risk boshqaruvini o'zingiz nazorat qiling."
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            print(f"[telegram_bot.py] Xabar yuborilmadi: {response.text}")
    except requests.RequestException as e:
        print(f"[telegram_bot.py] So'rov xatosi: {e}")
