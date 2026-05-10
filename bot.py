
import requests
import os
import time
import json

TOKEN = os.getenv("BOT_TOKEN")
LAST_UPDATE = 0

CARD_NUMBER = "1234-5678-9012-3456"  # شماره کارت پیش‌فرض که میتونی تغییرش بدی
ADMIN_ID = 123456789  # شماره تلگرام خودت
orders = {}  # اطلاعات سفارش: chat_id -> {"gigs": int, "price": int, "paid": False, "receipt": None, "delivered": False}

def send_message(chat_id, text, buttons=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        payload["reply_markup"] = json.dumps({"inline_keyboard": buttons})
    requests.post(url, json=payload)

def answer_callback(callback_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    requests.post(url, json={"callback_query_id": callback_id, "text": text, "show_alert": True})

def bot_loop():
    global LAST_UPDATE
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={LAST_UPDATE + 1}&timeout=10"
            response = requests.get(url).json()

            for update in response.get("result", []):
                LAST_UPDATE = update["update_id"]

                # پیام معمولی
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    if "photo" in message:  # عکس رسید
                        if chat_id in orders and orders[chat_id].get("paid") and not orders[chat_id].get("delivered"):
                            orders[chat_id]["receipt"] = message["photo"][-1]["file_id"]
                            send_message(chat_id, "رسید شما دریافت شد ✅ لطفا منتظر تایید پشتیبانی باشید")
                            send_message(ADMIN_ID, f"کاربر {chat_id} رسید پرداخت {orders[chat_id]['price']:,} تومان را ارسال کرد.")
                    elif text == "/start":
                        buttons = [
                            [{"text": "خرید VPN", "callback_data": "buy"}],
                            [{"text": "وضعیت سرور", "callback_data": "status"}]
                        ]
                        send_message(chat_id, "ربات VPN روشنه ✅\nیک گزینه انتخاب کن:", buttons)

                # دکمه‌های Inline
                if "callback_query" in update:
                    callback = update["callback_query"]
                    callback_id = callback["id"]
                    data = callback["data"]
                    chat_id = callback["message"]["chat"]["id"]

                    # خرید VPN
                    if data == "buy":
                        buttons = [
                            [{"text": "1 گیگ", "callback_data": "1"}],
                            [{"text": "2 گیگ", "callback_data": "2"}],
                            [{"text": "3 گیگ", "callback_data": "3"}]
                        ]
                        send_message(chat_id, "چند گیگ VPN میخوای؟", buttons)
                        answer_callback(callback_id, "سایز VPN رو انتخاب کن")

                    # انتخاب حجم
                    elif data in ["1","2","3"]:
                        gigs = int(data)
                        price = gigs * 350_000
                        orders[chat_id] = {"gigs": gigs, "price": price, "paid": False, "receipt": None, "delivered": False}
                        buttons = [[{"text": "کارت به کارت", "callback_data": "pay"}]]
                        send_message(chat_id, f"{gigs} گیگ VPN قیمتش {price:,} تومان است 💰\nروش پرداخت رو انتخاب کن:", buttons)
                        answer_callback(callback_id, f"{gigs} گیگ انتخاب شد")

                    # کارت به کارت
                    elif data == "pay":
                        send_message(chat_id, f"شماره کارت برای واریز:\n<b>{CARD_NUMBER}</b>\nبعد از واریز رسید را به ربات ارسال کنید و روی دکمه 'پرداخت کردم و عکس رسید' بزنید")
                        buttons = [[{"text": "پرداخت کردم و عکس رسید", "callback_data": "paid"}]]
                        send_message(chat_id, "وقتی پرداخت کردی روی دکمه زیر بزن:", buttons)
                        answer_callback(callback_id, "لینک کارت داده شد")

                    # پرداخت انجام شد
                    elif data == "paid":
                        if chat_id in orders:
                            orders[chat_id]["paid"] = True
                            send_message(chat_id, "رسید شما ثبت شد ✅ لطفا منتظر تایید پشتیبانی باشید")
                            send_message(ADMIN_ID, f"کاربر {chat_id} پرداخت {orders[chat_id]['price']:,} تومان را اعلام کرد و رسید آماده بررسی است.")
                        answer_callback(callback_id, "پرداخت ثبت شد")

                    # وضعیت سرور
                    elif data == "status":
                        send_message(chat_id, "سرورهای VPN همگی آنلاین هستند ✅")
                        answer_callback(callback_id, "وضعیت سرورها")

        except Exception as e:
            print("خطا:", e)
        time.sleep(1)

if __name__ == "__main__":
    bot_loop()
