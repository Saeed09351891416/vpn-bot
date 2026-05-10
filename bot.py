import requests
import os
import time

# توکن ربات تلگرام از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN")
LAST_UPDATE = 0

def send_message(chat_id, text):
    """ارسال پیام به کاربر"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def bot_loop():
    """حلقه اصلی ربات"""
    global LAST_UPDATE
    while True:
        try:
            # گرفتن آپدیت‌ها از تلگرام
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={LAST_UPDATE + 1}"
            response = requests.get(url).json()
            
            for update in response.get("result", []):
                LAST_UPDATE = update["update_id"]
                
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    
                    # پاسخ به دستور /start
                    if text == "/start":
                        send_message(chat_id, "سلام! ربات فعال شد ✅")
                        
        except Exception as e:
            print("خطا:", e)
        
        # کمی صبر بین حلقه‌ها
        time.sleep(1)

if __name__ == "__main__":
    bot_loop()
