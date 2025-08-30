# bot.py — aiogram 3.x + Flask keep-alive for Render (120 концовок, без случайных смертей)
import os
import asyncio
import logging
import threading
from flask import Flask

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

# =========================
# ENV & LOGGING
# =========================
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN", "PASTE_YOUR_TOKEN_HERE")
PORT = int(os.getenv("PORT", "8080"))

if not TOKEN or TOKEN == "PASTE_YOUR_TOKEN_HERE":
    print("⚠️ Поставь токен в переменную окружения TELEGRAM_TOKEN!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# Flask keep-alive (Render)
# =========================
app = Flask(__name__)

@app.route("/")
def index():
    return "Бот работает! 💡"

def run_web():
    app.run(host="0.0.0.0", port=PORT)

threading.Thread(target=run_web, daemon=True).start()

# =========================
# GAME DATA (детерминированно, 120 концовок)
# =========================
user_state: dict[int, dict] = {}  # { user_id: {"scene": str, "history": [str,...]} }

def kb(options: dict | None) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    if not options:
        # финалка: показываем /restart и кнопку назад (на случай, если игрок захочет отыграть последний шаг)
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="/restart")],
                [KeyboardButton(text="⬅️ Назад")],
            ],
            resize_keyboard=True,
        )
    rows = [[KeyboardButton(text=opt)] for opt in options.keys()]
    rows.append([KeyboardButton(text="⬅️ Назад")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def ending(text: str) -> str:
    return f"{text}\n\n/restart - начать заново"

# Базовые тексты смертей, будем циклически использовать
DEATH_LINES = [
    "⚰️ Твоя история оборвалась в тишине.",
    "💀 Последний выбор оказался роковым.",
    "☠️ Всё закончилось слишком быстро.",
    "🌑 Ночь накрыла тебя окончательно.",
    "🔥 Искра жизни погасла.",
    "🕯 Свеча судьбы догорела.",
    "🧊 Сердце застыло без слов.",
    "🕳 Тьма поглотила тебя.",
    "🪦 На этом пути не было возврата.",
    "⚡ Судьба ударила без предупреждения.",
    "🌀 Мир сомкнулся над тобой.",
    "🧩 Пазл жизни не сложился.",
    "🌫 Ты растворился в тумане событий.",
    "🛑 Красный свет так и не сменился.",
    "🌋 Поток обстоятельств смёл тебя.",
]

# Инициализируем квест-словарь
quest: dict[str, dict] = {
    "start": {
        "text": "Ты просыпаешься в обычный день. Куда направишь жизнь?",
        "options": {
            "🎓 Школа и экзамены": "H_SCHOOL",
            "🏠 Дом и быт": "H_HOME",
            "🌆 Улица и город": "H_CITY",
            "💼 Карьера и деньги": "H_CAREER",
        }
    },
    # Хабы верхнего уровня
    "H_SCHOOL": {
        "text": "Школьные коридоры и запах доски. С чего начнёшь?",
        "options": {f"Ветка школы #{i}": f"S{i}" for i in range(1, 11)}  # S1..S10
    },
    "H_HOME": {
        "text": "Домашний уют не всегда безопасен. Куда потянет?",
        "options": {f"Ветка дома #{i}": f"S{i}" for i in range(11, 21)}  # S11..S20
    },
    "H_CITY": {
        "text": "Шумный город полон случайных встреч. Выбирай направление.",
        "options": {f"Ветка города #{i}": f"S{i}" for i in range(21, 31)}  # S21..S30
    },
    "H_CAREER": {
        "text": "Кабинеты, дедлайны, амбиции. Что впереди?",
        "options": {f"Ветка карьеры #{i}": f"S{i}" for i in range(31, 41)}  # S31..S40
    },
}

# Наполняем 40 «подхабов» S1..S40, каждый с 3 выбором — итого 120 концовок
# Sx -> {A,B,C} -> D(x,1..3) (каждый — финал со смертью)
# Для разнообразия зададим разные подпиcи.
CHOICES = [
    ("A", "Пойти напролом"),
    ("B", "Осторожно обойти"),
    ("C", "Довериться случаю"),
]

ending_counter = 0
for s in range(1, 41):  # S1..S40
    skey = f"S{s}"
    # Текст подхаба — разный по зоне
    if 1 <= s <= 10:
        hub_text = f"Школа — ветка #{s}. Экзамены, друзья, спорт, давление взрослых. Как поступишь?"
    elif 11 <= s <= 20:
        hub_text = f"Дом — ветка #{s}. Семья, соседи, быт, неожиданные звонки. Что выберешь?"
    elif 21 <= s <= 30:
        hub_text = f"Город — ветка #{s}. Метро, бандиты, витрины, подворотни. Твой следующий шаг?"
    else:
        hub_text = f"Карьера — ветка #{s}. Собеседования, начальники, сделки, кредиты. Продолжим?"

    quest[skey] = {"text": hub_text, "options": {}}

    for idx, (letter, caption) in enumerate(CHOICES, start=1):
        ending_counter += 1
        dkey = f"D{s}_{idx}"  # уникальная концовка
        death_line = DEATH_LINES[(ending_counter - 1) % len(DEATH_LINES)]
        # Разнообразим подпись финала лёгким контекстом
        if 1 <= s <= 10:
            context = "Школьный звонок прозвенел в последний раз."
        elif 11 <= s <= 20:
            context = "Домашний свет погас навсегда."
        elif 21 <= s <= 30:
            context = "Городские огни больше не манят."
        else:
            context = "Погоня за карьерой закончилась пустотой."

        quest[dkey] = {
            "text": ending(f"{death_line}\n\n{context}"),
            "options": {}
        }
        quest[skey]["options"][f"{caption}"] = dkey

# Дополнительные «ручные» сцены для вкуса (всё равно ведут в хабы)
quest["school_entry"] = {
    "text": "Ты стоишь у двери в кабинет. Вдох-выдох. Шагнуть внутрь?",
    "options": {
        "Войти и сдать тест": "H_SCHOOL",
        "Развернуться домой": "H_HOME",
        "Свернуть к метро": "H_CITY",
    }
}
quest["home_entry"] = {
    "text": "Ключ поворачивается в замке. Тишина. Что дальше?",
    "options": {
        "Позвонить родителям": "H_HOME",
        "Включить новости и выйти": "H_CITY",
        "Открыть ноутбук и работать": "H_CAREER",
    }
}

# Свяжем старт ещё и с ручными входами
quest["start"]["options"]["🚪 Зайти в кабинет"] = "school_entry"
quest["start"]["options"]["🔑 Открыть входную дверь"] = "home_entry"


async def send_scene(user_id: int, message: Message):
    node = quest[user_state[user_id]["scene"]]
    await message.answer(node["text"], reply_markup=kb(node.get("options")))

# =========================
# HANDLERS
# =========================
@dp.message(Command("start", "restart"))
async def cmd_start(message: Message):
    user_state[message.from_user.id] = {"scene": "start", "history": []}
    await send_scene(message.from_user.id, message)

@dp.message(F.text == "⬅️ Назад")
async def cmd_back(message: Message):
    data = user_state.get(message.from_user.id)
    if not data or not data["history"]:
        await message.answer("Назад нельзя.", reply_markup=ReplyKeyboardRemove())
        return
    data["scene"] = data["history"].pop()
    await send_scene(message.from_user.id, message)

@dp.message()
async def handle_choice(message: Message):
    uid = message.from_user.id
    data = user_state.setdefault(uid, {"scene": "start", "history": []})
    current = quest[data["scene"]]
    options = current.get("options", {})

    # Команда /restart текстом (на случай, если клавы нет)
    if message.text.strip() == "/restart":
        await cmd_start(message)
        return

    if message.text not in options:
        await message.answer("Выбери один из вариантов на клавиатуре.")
        return

    # Сохраняем историю и двигаемся
    data["history"].append(data["scene"])
    data["scene"] = options[message.text]
    await send_scene(uid, message)

# =========================
# RUN
# =========================
async def main():
    print("Бот запущен… концовок:", sum(1 for k, v in quest.items() if not v.get("options")))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

