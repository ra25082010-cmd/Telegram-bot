import os
import time
import requests

TOKEN = os.getenv("8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI") or "8432021119:AAFDrdxUIJSoIG1uMLPXNY6UGQP11pxPIeI"
ADMIN_ID = int(os.getenv("8263761630") or 8263761630)  # замени на свой Telegram ID

API = f"https://api.telegram.org/bot{TOKEN}"

OFFSET_FILE = "offset.dat"
processed = set()

def load_offset():
    try:
        return int(open(OFFSET_FILE).read().strip())
    except:
        return None

def save_offset(x):
    try:
        open(OFFSET_FILE, "w").write(str(int(x)))
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
        print("Ошибка при getUpdates:", e)
        return {}


def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        requests.post(API + "/sendMessage", data=data)
    except Exception as e:
        print("Ошибка при sendMessage:", e)


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
            uid = upd["update_id"]
            if uid in processed:
                offset = uid + 1
                save_offset(offset)
                continue

            processed.add(uid)
            if len(processed) > 2000:
                processed = set(list(processed)[-1000:])

            offset = uid + 1
            save_offset(offset)

            msg = upd.get("message")
            if not msg:
                continue

            chat_id = msg["chat"]["id"]
            text = msg.get("text", "").strip()

            if text == "/start":
                send_message(chat_id, "👋 Привет! Возможно я занят, оставь свой вопрос отвечу позже!")
            elif text == "/ping":
                send_message(chat_id, "🏓 Бот на связи!")
            elif text == "/admin" and chat_id == ADMIN_ID:
                send_message(chat_id, "⚙️ Админ-панель:\n\n/start — приветствие\n/ping — пинг\n/users — список пользователей\n/stop — выключить бота")
            elif text == "/stop" and chat_id == ADMIN_ID:
                send_message(chat_id, "🛑 Бот остановлен администратором.")
                print("Бот остановлен вручную.")
                return
            else:
                send_message(chat_id, "🤖 Неизвестная команда. Используй /start или /ping")

        time.sleep(0.5)


if __name__ == "__main__":
    # убедись, что webhook отключён
    try:
        requests.get(API + "/deleteWebhook")
    except:
        pass

    main()
