import requests
import time
import traceback
from datetime import datetime

TOKEN = "8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI"
ADMIN_ID = 8263761630  # вставь свой Telegram ID
URL = f"https://api.telegram.org/bot{TOKEN}/"

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    return requests.get(URL + "getUpdates", params=params).json()

def send_message(chat_id, text):
    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text})

def main():
    print("Бот запущен ✅")
    offset = None
    send_message(ADMIN_ID, "🚀 Бот запущен на Render и работает 24/7!")

    while True:
        try:
            updates = get_updates(offset)
            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")

                print(f"[{now()}] {chat_id}: {text}")
                if text == "/start":
                    send_message(chat_id, "Привет! Я живу на Render 🌐")
                elif text == "/ping":
                    send_message(chat_id, "🏓 Pong!")
                elif text == "/stop" and chat_id == ADMIN_ID:
                    send_message(chat_id, "⛔ Отключаюсь по команде администратора.")
                    return
                else:
                    send_message(chat_id, "Я получил твоё сообщение 😉")

        except Exception as e:
            print("Ошибка:", e)
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    main()
