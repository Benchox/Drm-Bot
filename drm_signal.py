import os
import requests

TELEGRAM_TOKEN = os.environ.get("8804602899:AAHhPxCDmJax8v4v3wl1yTTIwtLjEQrclyY")
CHAT_ID = os.environ.get("1780797125")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("Status code:", r.status_code)
        print("Response:", r.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    send_telegram("✅ <b>TEST</b> Bot DRM berhasil terhubung! 🚀")
    print("Pesan dikirim")
