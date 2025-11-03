import os
import time
import requests
from datetime import datetime

TOKEN = os.getenv("8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI") or "8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI"
ADMIN_ID = int(os.getenv("8263761630") or 8263761630)  # твой Telegram ID

API = f"https://api.telegram.org/bot{TOKEN}"

OFFSET_FILE = "offset.dat"
LOG_FILE = "bot.log"

processed_ids = set()
users = set()


def log_event(text, alert_admin=False):
    """Запись лога и (опционально) уведомление админу."""
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    if alert_admin:
        send_message(ADMIN_ID, f"🪵 {text}")


def load_offset():
    try:
        return int(open(OFFSET_FILE).read().strip())
    except:
        return None


def save_offset(x):
    try:
        with open(OFFSET_FILE, "w") as f:
            f.write(str(int(x)))
    except:
        pass


def get_updates(offset=None, timeout=20):
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(API + "/getUpdates", params=params, timeout=30)
        return r.json()
    except Exception as e:
        log_event(f"Ошибка getUpdates: {e}", alert_admin=True)
        return {}


def send_message(chat_id, text):
    try:
        requests.post(API + "/sendMessage", data={"chat_id": chat_id, "text": text})
    except Exception as e:
        log_event(f"Ошибка sendMessage: {e}", alert_admin=True)


def main():
    log_event("✅ Бот запущен и работает 24/7", alert_admin=True)
    offset = load_offset()

    while True:
        updates = get_updates(offset)
        results = updates.get("result", [])
        if not results:
            time.sleep(1)
            continue

        for upd in results:
            update_id = upd["update_id"]
            offset = update_id + 1
            save_offset(offset)

            if update_id in processed_ids:
                continue
            processed_ids.add(update_id)

            msg = upd.get("message")
            if not msg:
                continue

            chat_id = msg["chat"]["id"]
            text = msg.get("text", "").strip()
            username = msg["from"].get("username", "без никнейма")

            # лог всех входящих сообщений
            log_event(f"📩 @{username} ({chat_id}): {text}")

            # сохраняем пользователя
            users.add(chat_id)

            # ===== Админ отвечает пользователям =====
            if chat_id == ADMIN_ID and text.startswith("/reply"):
                parts = text.split(maxsplit=2)
                if len(parts) < 3:
                    send_message(ADMIN_ID, "❗ Формат: /reply <user_id> <текст>")
                else:
                    try:
                        target_id = int(parts[1])
                        reply_text = parts[2]
                        send_message(target_id, f"💬 Ответ от администратора:\n{reply_text}")
                        send_message(ADMIN_ID, f"✅ Ответ отправлен пользователю {target_id}")
                        log_event(f"✉️ Админ ответил пользователю {target_id}: {reply_text}")
                    except Exception as e:
                        log_event(f"⚠️ Ошибка при ответе: {e}", alert_admin=True)
                continue

            # ===== Команды =====
            if text == "/start":
                send_message(chat_id, "👋 Привет! Я бот, который работает на Render 24/7.")
            elif text == "/ping":
                send_message(chat_id, "🏓 Бот на связи!")
            elif text == "/admin" and chat_id == ADMIN_ID:
                send_message(chat_id, "⚙️ Админ-панель:\n\n/users — список пользователей\n/reply <id> <текст> — ответить\n/stop — выключить бота")
            elif text == "/users" and chat_id == ADMIN_ID:
                user_list = "\n".join(map(str, users)) or "Нет пользователей"
                send_message(chat_id, f"👥 Пользователи:\n{user_list}")
            elif text == "/stop" and chat_id == ADMIN_ID:
                send_message(chat_id, "🛑 Бот остановлен.")
                log_event("❌ Бот остановлен вручную", alert_admin=True)
                return
            else:
                # пользователь пишет
                if chat_id != ADMIN_ID:
                    send_message(ADMIN_ID, f"💬 @{username} (ID {chat_id}): {text}")
                    send_message(chat_id, "✅ Сообщение получено. Администратор скоро ответит.")
                else:
                    send_message(chat_id, "🤖 Неизвестная команда. Используй /ping или /users")

        time.sleep(0.5)


if __name__ == "__main__":
    try:
        requests.get(API + "/deleteWebhook")
    except:
        pass

    main()
