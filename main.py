import requests
import datetime
import traceback
import time
from keep_alive import keep_alive

TELEGRAM_BOT_TOKEN = "8041985955:AAGNPL_dWWWI5AWlYFue5NxkNOXsYqBOmiw"
TELEGRAM_CHANNEL_ID = "@PumpGuardians"

SEEN_MINTS = set()

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    print("[DEBUG] Sending message to Telegram...")
    print(f"[DEBUG] Payload: {payload}")
    try:
        response = requests.post(url, data=payload)
        print(f"[DEBUG] Telegram response status: {response.status_code}")
        print(f"[DEBUG] Telegram response body: {response.text}")

        if response.status_code != 200:
            print("[ERROR] Failed to send message to Telegram.")
        else:
            print("[SUCCESS] Message sent successfully.")
    except Exception as e:
        print("[EXCEPTION] Telegram send failed:")
        traceback.print_exc()

def format_token_message(info):
    try:
        address = info.get("address", "")
        if not address:
            print("[SKIP] No address found.")
            return None
        if address in SEEN_MINTS:
            print(f"[SKIP] Already seen token: {address}")
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
            f"<b>PUMP GUARDIANS AI</b>\n\n"
            f"<b>{name} / {symbol}</b>\n"
            f"{green_circles}\n\n"
            f"💵 <b>Price:</b> ${price_usd:.4f} ({price_sol:.4f} SOL)\n"
            f"💰 <b>Market Cap:</b> ${market_cap:,.0f}\n"
            f"📈 <b>Volume:</b> {volume:,.0f} SOL\n"
            f"👥 <b>Holders:</b> {holders}\n"
            f"⏱️ <b>Age:</b> {age_str}\n"
            f"🌐 <b>Website:</b> {website}\n"
            f"🐦 <b>Twitter:</b> {twitter}\n\n"
            f"<a href='https://pump.fun/{address}'>Buy</a> | "
            f"<a href='https://www.dexscreener.com/solana/{address}'>Chart</a> | "
            f"<a href='https://birdeye.so/token/{address}'>More Info</a>"
        )
        print("[DEBUG] Message formatted successfully.")
        return message

    except Exception as e:
        print("[ERROR] Failed to format message:")
        traceback.print_exc()
        return None

def fetch_latest_tokens():
    url = "https://pumpportal.fun/api/trending"
    print(f"[DEBUG] Fetching trending tokens from {url}")
    try:
        response = requests.get(url)
        print(f"[DEBUG] Trending API status: {response.status_code}")
        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch trending tokens: {response.text}")
            return []
        data = response.json()
        print(f"[DEBUG] Received {len(data)} tokens.")
        return data if isinstance(data, list) else []
    except Exception:
        print("[ERROR] Exception while fetching trending tokens:")
        traceback.print_exc()
        return []

def main_loop():
    while True:
        print("===========================================")
        print("[INFO] Checking for new tokens...")
        tokens = fetch_latest_tokens()

        for token in tokens:
            address = token.get("address")
            if not address:
                print("[SKIP] Token has no address.")
                continue
            if address in SEEN_MINTS:
                print(f"[SKIP] Already processed: {address}")
                continue

            full_info_url = f"https://pumpportal.fun/api/mint/{address}"
            print(f"[DEBUG] Fetching full info for {address}...")
            try:
                response = requests.get(full_info_url)
                print(f"[DEBUG] Detail API status: {response.status_code}")
                if response.status_code != 200:
                    print(f"[ERROR] Failed to get token detail: {response.text}")
                    continue
                info = response.json()
                msg = format_token_message(info)
                if msg:
                    send_telegram_message(msg)
                else:
                    print(f"[SKIP] Message was None for: {address}")
            except:
                print(f"[EXCEPTION] Error processing token {address}")
                traceback.print_exc()

        print("[SLEEP] Sleeping 20 seconds...\n")
        time.sleep(20)

if __name__ == "__main__":
    print("[STARTING] Bot is running.")
    keep_alive()
    main_loop()
