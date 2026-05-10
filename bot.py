
import requests
import os
import time
import json

TOKEN = os.getenv("BOT_TOKEN")
LAST_UPDATE = 0

def send_message(chat_id, text, buttons=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    
    if buttons:
        # اینجا reply_markup حتماً به JSON string تبدیل میشه
        payload["reply_markup"] = json.dumps({"inline_keyboard": buttons})
    
    requests.post(url, json=payload)

def answer_callback(callback_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    requests.post(url, json={"callback_query_id": callback_id, "text": text, "show_alert": True})

def bot_loop():
    global LAST_UPDATE
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={LAST_UPDATE + 1}"
            response = requests.get(url).json()
            
            for update in response.get("result", []):
                LAST_UPDATE = update["update_id"]
                
                # پیام‌های معمولی
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    
                    if text == "/start":
                        buttons = [
                            [{"text": "خرید VPN", "callback_data": "buy"}],
                            [{"text": "وضعیت سرور", "callback_data": "status"}]
                        ]
                        send_message(chat_id, "ربات VPN روشنه ✅\nیک گزینه انتخاب کن:", buttons)
                
                # دکمه‌های Inline (Callback Query)
                if "callback_query" in update:
                    callback = update["callback_query"]
                    callback_id = callback["id"]
                    data = callback["data"]
                    
                    if data == "buy":
                        answer_callback(callback_id, "برای خرید VPN با پشتیبانی تماس بگیرید 📩")
                    elif data == "status":
                        answer_callback(callback_id, "سرورهای VPN همگی آنلاین هستند ✅")
                    
        except Exception as e:
            print("خطا:", e)
        time.sleep(1)

if __name__ == "__main__":
    bot_loop()
