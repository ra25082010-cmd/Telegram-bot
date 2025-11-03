import time
import traceback
import requests
from datetime import datetime
import os
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 🔑 ВСТАВЬ свой токен от BotFather
TOKEN = "8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI"
# 🔑 ВСТАВЬ свой Telegram ID (для уведомлений)
ADMIN_ID = 8263761630

URL = f"https://api.telegram.org/bot{TOKEN}/"


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    return requests.get(URL + "getUpdates", params=params).json()


def send_message(chat_id, text):
    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text})


def main():
    print("✅ Бот запущен и работает 24/7 на Render!")
    send_message(ADMIN_ID, "🚀 Бот запущен на Render и готов к работе!")

    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")

                if not chat_id or not text:
                    continue

                print(f"[{now()}] {chat_id}: {text}")

                if text == "/start":
                    send_message(chat_id, "Привет! 🤖 Я живу на Render 🌐")
                elif text == "/ping":
                    send_message(chat_id, "🏓 Pong!")
                elif text == "/stop" and chat_id == ADMIN_ID:
                    send_message(chat_id, "🛑 Отключаюсь по команде администратора.")
                    return
                else:
                    send_message(chat_id, "Я получил твоё сообщение 😉")

        except Exception as e:
            print("Ошибка:", e)
            traceback.print_exc()
            time.sleep(5)


# 🔹 Запуск HTTP-сервера (нужен Render для "живости" проекта)
def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌐 Веб-сервер запущен на порту {port}")
    server.serve_forever()


if __name__ == "__main__":
    Thread(target=run_server).start()
    main()
