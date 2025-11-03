import time
import traceback
import requests
from datetime import datetime
import os
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 🔑 Твой токен
TOKEN = "8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI"
# 🔑 Твой Telegram ID (админ)
ADMIN_ID = 8263761630

URL = f"https://api.telegram.org/bot{TOKEN}/"

# 📂 Список пользователей хранится в памяти
users = set()

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    return requests.get(URL + "getUpdates", params=params).json()

def send_message(chat_id, text):
    requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text})

def broadcast(text):
    """Отправка всем пользователям"""
    for user_id in users:
        try:
            send_message(user_id, text)
        except:
            pass

def admin_help():
    return (
        "🧰 *Админ-панель*\n\n"
        "/stats — список пользователей 👥\n"
        "/broadcast — рассылка 💬\n"
        "/ping — проверка статуса ⚙️\n"
        "/stop — остановить бота 🛑"
    )

def main():
    print("✅ Бот запущен и работает на Render!")
    send_message(ADMIN_ID, "🚀 Бот запущен и готов к работе!")

    offset = None
    while True:
        try:
            updates = get_updates(offset)
            results = updates.get("result", [])

            for upd in results:
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")

                if not chat_id or not text:
                    continue

                users.add(chat_id)
                print(f"[{now()}] {chat_id}: {text}")
                offset = upd["update_id"] + 1

                # Команды пользователя
                if text == "/start":
                    send_message(chat_id, "Привет! 🤖 Я живу на Render 🌐")
                elif text == "/ping":
                    send_message(chat_id, "🏓 Pong!")

                # 🔒 Админ-панель
                elif chat_id == ADMIN_ID:
                    if text == "/admin":
                        send_message(chat_id, admin_help())
                    elif text == "/stats":
                        send_message(chat_id, f"👥 Пользователей: {len(users)}")
                    elif text.startswith("/broadcast "):
                        message = text.replace("/broadcast ", "").strip()
                        broadcast(f"📢 Сообщение от администратора:\n\n{message}")
                        send_message(chat_id, "✅ Рассылка завершена.")
                    elif text == "/stop":
                        send_message(chat_id, "🛑 Бот остановлен администратором.")
                        return
                else:
                    send_message(chat_id, "Я получил твоё сообщение 😉")

            time.sleep(1)

        except Exception as e:
            print("Ошибка:", e)
            traceback.print_exc()
            time.sleep(5)

# 🌐 Запуск веб-сервера для Render
def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌍 Веб-сервер запущен на порту {port}")
    server.serve_forever()

if __name__ == "__main__":
    Thread(target=run_server).start()
    main()
