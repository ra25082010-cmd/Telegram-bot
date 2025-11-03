import os
import time
import requests
import traceback
from datetime import datetime
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN", "8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI")  # или укажи через Render Environment
ADMIN_ID = int(os.getenv("ADMIN_ID", "8263761630"))  # твой Telegram ID
URL = f"https://api.telegram.org/bot{TOKEN}/"

# === Вспомогательные функции ===
def now():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def log(*args):
    print(now(), *args, flush=True)

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    try:
        resp = requests.get(URL + "getUpdates", params=params, timeout=120)
        return resp.json()
    except Exception as e:
        log("Ошибка get_updates:", e)
        return {}

def send_message(chat_id, text):
    try:
        requests.post(URL + "sendMessage", data={"chat_id": chat_id, "text": text})
    except Exception as e:
        log("Ошибка send_message:", e)

# === Основная логика ===
def main():
    log("✅ Бот запущен на Render и готов к работе.")
    send_message(ADMIN_ID, "🤖 Бот запущен и работает 24/7 на Render!")

    offset = None
    users = set()  # хранит ID пользователей

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

                # === лог сообщений ===
                user_name = msg.get("from", {}).get("username", "unknown")
                log(f"📩 {chat_id} ({user_name}): {text}")
                users.add(chat_id)

                # === команды ===
                if text == "/start":
                    send_message(chat_id, "👋 Привет! Я возможно я сейчас занят, оставь свой вопрос, отвечу когда освобождусь.")
                elif text == "/help":
                    send_message(chat_id, "📜 Команды:\n/start — начать\n/ping — проверить связь\n/help — помощь")
                elif text == "/ping":
                    send_message(chat_id, "🏓 Pong!")
                elif text == "/stop" and chat_id == ADMIN_ID:
                    send_message(chat_id, "🛑 Бот остановлен администратором.")
                    log("Бот остановлен админом.")
                    return
                elif chat_id == ADMIN_ID and text.startswith("/users"):
                    # список пользователей
                    if users:
                        send_message(chat_id, "👥 Пользователи:\n" + "\n".join(map(str, users)))
                    else:
                        send_message(chat_id, "Пока нет пользователей.")
                elif chat_id == ADMIN_ID and text.startswith("/send "):
                    # /send ID текст
                    try:
                        parts = text.split(" ", 2)
                        target_id = int(parts[1])
                        msg_text = parts[2]
                        send_message(target_id, f"📩 Сообщение от админа:\n{msg_text}")
                        send_message(chat_id, "✅ Сообщение отправлено.")
                    except Exception as e:
                        send_message(chat_id, f"⚠ Ошибка при отправке: {e}")
                else:
                    send_message(chat_id, "✅ Сообщение получено. Спасибо!")

        except Exception as e:
            log("Ошибка:", e)
            traceback.print_exc()
            time.sleep(5)

# === Web-сервер для Render ===
def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    log(f"🌐 Веб-сервер запущен на порту {port}")
    server.serve_forever()

if __name__ == "__main__":
    Thread(target=run_server).start()
    main()
