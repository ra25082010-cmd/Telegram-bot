import os
import time
import requests
import traceback
from datetime import datetime
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

# === Настройки ===
TOKEN = os.getenv("8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI", "8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI")  # замени токен или укажи в Render как переменную среды
ADMIN_ID = int(os.getenv("8263761630", "8263761630"))   # замени на свой Telegram ID
URL = f"https://api.telegram.org/bot{TOKEN}/"

# === Основные функции ===
def now():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    try:
        response = requests.get(URL + "getUpdates", params=params, timeout=120)
        return response.json()
    except Exception as e:
        print(now(), "Ошибка при получении обновлений:", e)
        return {}

def send_message(chat_id, text):
    try:
        requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(now(), "Ошибка при отправке сообщения:", e)

def main():
    print(now(), "✅ Бот запущен и работает на Render")
    send_message(ADMIN_ID, "🤖 Бот успешно запущен на Render и работает 24/7!")

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

                print(now(), f"{chat_id}: {text}")

                # === Команды ===
                if text == "/start":
                    send_message(chat_id, "👋 Привет! Я живу на Render и готов к работе.")
                elif text == "/ping":
                    send_message(chat_id, "🏓 Pong!")
                elif text == "/stop" and chat_id == ADMIN_ID:
                    send_message(chat_id, "🛑 Бот остановлен администратором.")
                    print(now(), "Бот остановлен админом.")
                    return
                else:
                    send_message(chat_id, "✅ Я получил твоё сообщение!")

        except Exception as e:
            print(now(), "Ошибка:", e)
            traceback.print_exc()
            time.sleep(5)

# === Web-сервер для Render ===
def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(now(), f"🌐 Веб-сервер запущен на порту {port}")
    server.serve_forever()

if __name__ == "__main__":
    Thread(target=run_server).start()
    main()
