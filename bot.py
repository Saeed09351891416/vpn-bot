from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import requests
import os
import time

TOKEN = os.getenv("BOT_TOKEN")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

LAST_UPDATE = 0

def bot_loop():
    global LAST_UPDATE

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={LAST_UPDATE + 1}"
            response = requests.get(url).json()

            for update in response["result"]:
                LAST_UPDATE = update["update_id"]

                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")

                    if text == "/start":
                        send_message(chat_id, "ربات VPN روشنه ✅")

        except Exception as e:
            print(e)

        time.sleep(2)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

PORT = int(os.environ.get("PORT", 10000))

threading.Thread(target=bot_loop).start()

server = HTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()
