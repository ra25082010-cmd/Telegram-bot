import time
import traceback
import requests
from datetime import datetime
import os
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 🔑 Токен и ID администратора
TOKEN = "8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI"
ADMIN_ID = 8263761630
URL = f"https://api.telegram.org/bot{TOKEN}/"

# 📂 Список пользователей
users = set()

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    try:
        return requests.get(URL + "getUpdates", params=params, timeout=120).json()
    except:
        return {}

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        data["reply_markup"] = reply_markup
    requests.post(URL + "sendMessage", json=data)

def broadcast(text):
    """Рассылка всем пользователям"""
    for user_id in users:
        try:
            send_message(user_id, f"📢 Сообщение от администратора:\n\n{text}")
        except:
            pass

def admin_menu():
    """Меню администратора"""
    return {
        "inline_keyboard": [
            [{"text": "👥 Статистика", "callback_data": "stats"}],
            [{"text": "💬 Рассылка", "callback_data": "broadcast"}],
            [{"text": "🏓 Проверка бота", "callback_data": "ping"}],
            [{"text": "🛑 Остановить бота", "callback_data": "stop"}],
        ]
    }

def main():
    print("✅ Бот запущен и работает на Render!")
    send_message(ADMIN_ID, "🚀 Бот запущен и готов к работе!")

    offset = None
    waiting_broadcast = False

    while True:
        try:
            updates = get_updates(offset)
            results = updates.get("result", [])

            if not results:
                continue  # ⏳ Нет новых сообщений

            for upd in results:
                offset = upd["update_id"] + 1  # ✅ Обновляем offset сразу
                msg = upd.get("message")
                query = upd.get("callback_query")

                # 💬 Сообщение
                if msg:
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    users.add(chat_id)

                    print(f"[{now()}] {chat_id}: {text}")

                    if waiting_broadcast and chat_id == ADMIN_ID:
                        broadcast(text)
                        send_message(chat_id, "✅ Рассылка завершена.")
                        waiting_broadcast = False
                        continue

                    if text == "/start":
                        send_message(chat_id, "Привет! Я сейчас занят, отвечу как смогу!")
                    elif text == "/ping":
                        send_message(chat_id, "🏓 Pong!")
                    elif text == "/admin" and chat_id == ADMIN_ID:
                        send_message(chat_id, "🧰 Админ-панель:", reply_markup=admin_menu())
                    else:
                        send_message(chat_id, "Я получил твоё сообщение 😉")

                # ⚙️ Кнопки (callback)
                elif query:
                    data = query["data"]
                    chat_id = query["message"]["chat"]["id"]

                    if chat_id != ADMIN_ID:
                        send_message(chat_id, "⛔ Только администратор может использовать меню.")
                        continue

                    if data == "stats":
                        send_message(chat_id, f"👥 Пользователей: {len(users)}")
                    elif data == "ping":
                        send_message(chat_id, "🏓 Бот активен и отвечает!")
                    elif data == "broadcast":
                        send_message(chat_id, "💬 Введи сообщение для рассылки:")
                        waiting_broadcast = True
                    elif data == "stop":
                        send_message(chat_id, "🛑 Бот остановлен администратором.")
                        return

            time.sleep(1)  # ⏱️ Маленькая пауза, чтобы не спамить API

        except Exception as e:
            print("Ошибка:", e)
            traceback.print_exc()
            time.sleep(5)

# 🌍 Сервер для Render
def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌐 Веб-сервер запущен на порту {port}")
    server.serve_forever()

if __name__ == "__main__":
    Thread(target=run_server).start()
    main()
