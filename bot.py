import telebot
import json
import os
from flask import Flask, request

TOKEN = "8294147360:AAFY0qqmFnYfOOa6rM7gHGeB7uI7Zodw7sw"
bot = telebot.TeleBot(TOKEN)
WEBHOOK_URL = "https://telebot-bonus-2.onrender.com/webhook"

DATA_FILE = "users.json"

# Загружаем данные
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# Главное меню
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 Узнать баланс")
    return markup

# Старт
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)

    if user_id in users:
        bot.send_message(message.chat.id, f"Привет, {users[user_id]['name']}! Что хочешь сделать?", reply_markup=main_menu())
    else:
        users[user_id] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username,
            "phone": None,
            "bonus": 0
        }
        save_data()
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = telebot.types.KeyboardButton("Отправить номер 📱", request_contact=True)
        markup.add(button)
        bot.send_message(message.chat.id, "Добро пожаловать! Чтобы получить 100 бонусов, отправь свой номер телефона:", reply_markup=markup)

# Получение номера
@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    user_id = str(message.from_user.id)
    if user_id in users:
        if users[user_id]["phone"] is None:
            users[user_id]["phone"] = message.contact.phone_number
            users[user_id]["bonus"] += 100
            save_data()
            bot.send_message(message.chat.id, f"Спасибо! Мы записали твой номер: {users[user_id]['phone']}\nТы получил 100 бонусов!", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, "Номер уже сохранён.", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Сначала напиши /start")

# Узнать баланс
@bot.message_handler(func=lambda message: message.text == "📊 Узнать баланс")
def check_balance(message):
    user_id = str(message.from_user.id)
    if user_id in users:
        bot.send_message(message.chat.id, f"У тебя {users[user_id]['bonus']} бонусов 💰")
    else:
        bot.send_message(message.chat.id, "Сначала напиши /start")

# Flask сервер для webhook
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def index():
    return "Бот работает!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
