
import requests
import datetime
import traceback
import time
import os
from keep_alive import keep_alive

TELEGRAM_BOT_TOKEN = os.getenv("8041985955:AAGNPL_dWWWI5AWlYFue5NxkNOXsYqBOmiw")
TELEGRAM_CHANNEL_ID = os.getenv("@PumpGuardians")

SEEN_MINTS = set()

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, data=payload)
        print(f"[Telegram] Status: {response.status_code}")
        if response.status_code != 200:
            print(f"[Telegram Error] Response: {response.text}")
    except Exception:
        print("[Telegram Exception]")
        traceback.print_exc()

def format_token_message(info):
    try:
        address = info.get("address", "")
        if not address or address in SEEN_MINTS:
            return None

        SEEN_MINTS.add(address)

        name = info.get("name", "?")
        symbol = info.get("symbol", "?")
        price_usd = float(info.get("usdMarketPrice", 0))
        price_sol = float(info.get("solMarketPrice", 0))
        volume = float(info.get("totalVolume", 0))
        market_cap = float(info.get("marketCapUsd", 0))
        holders = info.get("holders", "?")
        twitter = info.get("twitter", "Not available")
        website = info.get("website", "Not available")
        created_at = int(info.get("created_at", 0))
        green_circles = "🟢" * int(info.get("score", 3))

        age_str = "Unknown"
        if created_at:
            age_seconds = int(datetime.datetime.now().timestamp()) - created_at
            age_minutes = age_seconds // 60
            age_str = f"{age_minutes} min ago"

        message = (
            f"<b>PUMP GUARDIANS AI</b>

"
            f"<b>{name} / {symbol}</b>
"
            f"{green_circles}

"
            f"💵 <b>Price:</b> ${price_usd:.4f} ({price_sol:.4f} SOL)
"
            f"💰 <b>Market Cap:</b> ${market_cap:,.0f}
"
            f"📈 <b>Volume:</b> {volume:,.0f} SOL
"
            f"👥 <b>Holders:</b> {holders}
"
            f"⏱️ <b>Age:</b> {age_str}
"
            f"🌐 <b>Website:</b> {website}
"
            f"🐦 <b>Twitter:</b> {twitter}

"
            f"<a href='https://pump.fun/{address}'>Buy</a> | "
            f"<a href='https://www.dexscreener.com/solana/{address}'>Chart</a> | "
            f"<a href='https://birdeye.so/token/{address}'>More Info</a>"
        )
        return message

    except Exception:
        print("[Format Error]")
        traceback.print_exc()
        return None

def fetch_latest_tokens():
    url = "https://pumpportal.fun/api/trending"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[ERROR] Cannot fetch trending tokens: {response.text}")
            return []
        data = response.json()
        return data if isinstance(data, list) else []
    except Exception:
        print("[Fetch Error]")
        traceback.print_exc()
        return []

def main_loop():
    while True:
        print("[INFO] Checking for new tokens...")
        tokens = fetch_latest_tokens()

        for token in tokens:
            address = token.get("address")
            if not address or address in SEEN_MINTS:
                continue

            full_info_url = f"https://pumpportal.fun/api/mint/{address}"
            try:
                response = requests.get(full_info_url)
                if response.status_code != 200:
                    continue
                info = response.json()
                msg = format_token_message(info)
                if msg:
                    send_telegram_message(msg)
            except:
                traceback.print_exc()

        time.sleep(20)

if __name__ == "__main__":
    keep_alive()
    main_loop()
