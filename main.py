import os
import time
import requests

TOKEN = os.getenv("8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI") or "8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI"
ADMIN_ID = int(os.getenv("8263761630") or 8263761630)  # твой Telegram ID

API = f"https://api.telegram.org/bot{TOKEN}"

OFFSET_FILE = "offset.dat"
processed_ids = set()
users = set()


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
        print("Ошибка getUpdates:", e)
        return {}


def send_message(chat_id, text):
    try:
        requests.post(API + "/sendMessage", data={"chat_id": chat_id, "text": text})
    except Exception as e:
        print("Ошибка sendMessage:", e)


def main():
    print("✅ Бот запущен и работает 24/7")
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

            # Сохраняем пользователя
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
                    except Exception as e:
                        send_message(ADMIN_ID, f"⚠️ Ошибка при ответе: {e}")
                continue

            # ===== Команды =====
            if text == "/start":
                send_message(chat_id, "👋 Привет! Я бот, который работает 24/7 на Render.")
            elif text == "/ping":
                send_message(chat_id, "🏓 Бот на связи!")
            elif text == "/admin" and chat_id == ADMIN_ID:
                send_message(chat_id, "⚙️ Админ-панель:\n\n/users — список пользователей\n/reply <id> <текст> — ответить\n/stop — выключить бота")
            elif text == "/users" and chat_id == ADMIN_ID:
                send_message(chat_id, "👥 Пользователи:\n" + "\n".join(map(str, users)))
            elif text == "/stop" and chat_id == ADMIN_ID:
                send_message(chat_id, "🛑 Бот остановлен.")
                print("Бот остановлен вручную.")
                return
            else:
                # если пользователь пишет
                if chat_id != ADMIN_ID:
                    send_message(ADMIN_ID, f"💬 @{username} (ID {chat_id}): {text}")
                    send_message(chat_id, "✅ Сообщение получено. Администратор скоро ответит.")
                else:
                    send_message(chat_id, "🤖 Неизвестная команда. Используй /ping или /users")

        time.sleep(0.5)


if __name__ == "__main__":
    # отключаем вебхук, чтобы не было дублей
    try:
        requests.get(API + "/deleteWebhook")
    except:
        pass

    main()
