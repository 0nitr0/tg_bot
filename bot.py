# bot.py — aiogram 3.x + Flask keep-alive for Render
import os
import asyncio
import logging
import random
import threading
from flask import Flask

from aiogram import Bot, Dispatcher
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

TOKEN = os.getenv("TELEGRAM_TOKEN", "7641482807:AAHfpmCKyIozprig39kzozh8lPeDCufijZE")  # Render: set env TELEGRAM_TOKEN
PORT = int(os.getenv("PORT", "8080"))                         # Render provides PORT for web

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
# GAME DATA
# =========================
# состояние игрока: scene + стек истории
user_state: dict[int, dict] = {}

def end_text(base: str) -> str:
    return f"{base}\n\n/restart - начать заново"

death_reasons = [
    "тебя сбила машина", "на тебя упал метеорит", "пришельцы похитили тебя",
    "призрак охладел твоё сердце", "ты умер от скуки", "тебя предали друзья",
    "тебя съел гигантский паук", "твоё сердце остановилось", "взрыв уничтожил всё вокруг",
    "ты растворился во времени", "древний культ принёс тебя в жертву",
    "неправильный химический эксперимент взорвался", "лестница внезапно оборвалась",
    "в лифте отключилось притяжение", "ты шагнул в неверную реальность",
    "бесконечная реклама довела до летального исхода", "умер от перфекционизма",
    "голем из бетона раздавил тебя", "система решила удалить тебя как баг",
    "ты не прошёл проверку на человечность",
]

def death_line() -> str:
    reason = random.choice(death_reasons)
    variants = [
        f"⚰️ Ты умер, потому что {reason}.",
        f"☠️ Конец. Причина: {reason}.",
        f"💀 Жизнь оборвалась — {reason}.",
        f"🔥 Последний миг настал: {reason}.",
    ]
    return end_text(random.choice(variants))

# Каркас квеста
quest: dict[str, dict] = {
    "start": {
        "text": "Ты просыпаешься в реальности выборов. С чего начнёшь?",
        "options": {
            "Сдать школьный тест": "school_test",
            "Искать первую подработку": "job_search",
            "Пойти в парк": "park_intro",
            "Остаться дома": "home_intro",
        },
    },

    # Немного именованных сцен (жизненные темы + наследство)
    "school_test": {
        "text": "Учитель раздаёт тесты. Твои действия?",
        "options": {
            "Списать у соседа": "caught_cheat",
            "Честно решать": "honest_pass",
            "Прогулять экзамен": "skip_exam",
        },
    },
    "caught_cheat": {
        "text": death_line(),
        "options": {},
    },
    "honest_pass": {
        "text": "Ты сдал достойно. Куда дальше повернёт жизнь?",
        "options": {
            "Университет": "uni_path",
            "Карьера сразу": "career_now",
            "Путешествовать автостопом": "travel_start",
        },
    },
    "skip_exam": {
        "text": death_line(),
        "options": {},
    },

    "uni_path": {
        "text": "Сессии, проекты, выбор специализации?",
        "options": {
            "Data Science": "ds_track",
            "Биомедицина": "bio_track",
            "Искусство": "art_track",
            "Бросить универ": "drop_uni",
        },
    },
    "career_now": {
        "text": "Первая работа, мало сна. Что приоритет?",
        "options": {
            "Деньги любой ценой": "money_max",
            "Баланс": "balance_life",
            "Семья": "family_start",
        },
    },
    "travel_start": {
        "text": "Дороги, случайные попутчики, вечерний автостоп...",
        "options": {
            "Ехать дальше в ночь": "night_ride",
            "Остановиться у костра": "camp_fire",
            "Вернуться домой": "home_intro",
        },
    },

    "ds_track": {"text": death_line(), "options": {}},
    "bio_track": {"text": death_line(), "options": {}},
    "art_track": {"text": death_line(), "options": {}},
    "drop_uni": {"text": death_line(), "options": {}},

    "money_max": {"text": death_line(), "options": {}},
    "balance_life": {"text": death_line(), "options": {}},

    "family_start": {
        "text": "Годы спустя вопрос наследства. На кого оформить?",
        "options": {
            "На старшего сына": "will_son",
            "На младшую дочь": "will_daughter",
            "Поровну на всех": "will_split",
            "На благотворительный фонд": "will_fund",
        },
    },
    "will_son": {"text": death_line(), "options": {}},
    "will_daughter": {"text": death_line(), "options": {}},
    "will_split": {"text": death_line(), "options": {}},
    "will_fund": {"text": death_line(), "options": {}},

    "night_ride": {"text": death_line(), "options": {}},
    "camp_fire": {"text": death_line(), "options": {}},

    "job_search": {
        "text": "Подработки: курьер, бариста, фриланс?",
        "options": {
            "Курьер": "courier_path",
            "Бариста": "barista_path",
            "Фриланс": "freelance_path",
        },
    },
    "courier_path": {"text": death_line(), "options": {}},
    "barista_path": {"text": death_line(), "options": {}},
    "freelance_path": {"text": death_line(), "options": {}},

    "park_intro": {
        "text": "В парке к тебе подходит странный человек...",
        "options": {
            "Поговорить": "mystery_person",
            "Игнорировать": "ignore_stranger",
            "Попросить совета": "ask_advice",
        },
    },
    "mystery_person": {"text": death_line(), "options": {}},
    "ignore_stranger": {"text": death_line(), "options": {}},
    "ask_advice": {"text": death_line(), "options": {}},

    "home_intro": {
        "text": "Дома тихо. В голове тысячи мыслей. Что сделать?",
        "options": {
            "Начать дневник": "journal_start",
            "Позвонить родителям": "call_parents",
            "Лечь спать": "sleep_now",
        },
    },
    "journal_start": {"text": death_line(), "options": {}},
    "call_parents": {"text": death_line(), "options": {}},
    "sleep_now": {"text": death_line(), "options": {}},
}

# Секретные концовки (мистика/НЛО) — тоже смерть
secret_nodes = {
    "secret_ufo": end_text("👽 НЛО вырвало тебя из реальности. В холодном космосе дыхание кончилось."),
    "secret_cult": end_text("🕯 Древний культ нашёл тебя. Ритуал завершён."),
    "secret_time": end_text("⏳ Ты застрял вне времени и… исчез."),
    "secret_glitch": end_text("🧩 Мир оказался симуляцией. Тебя удалили как ошибку."),
}

for key, text in secret_nodes.items():
    quest[key] = {"text": text, "options": {}}

# Автогенерация огромного числа сцен и смертей
NUM_SCENES = 400            # при желании увеличивай до 800+ (осторожно с памятью)
CHOICES_PER_SCENE = 4
CONTINUE_PROB = 0.35        # шанс, что выбор ведёт дальше, не к смерти

random_death_keys: list[str] = []

for i in range(1, NUM_SCENES + 1):
    scene_key = f"S{i}"
    quest[scene_key] = {"text": f"Сцена #{i}. Твой выбор?", "options": {}}
    for j in range(1, CHOICES_PER_SCENE + 1):
        if random.random() < CONTINUE_PROB and i < NUM_SCENES - 1:
            # переходим в любую более позднюю сцену
            nxt = f"S{random.randint(i + 1, NUM_SCENES)}"
            quest[scene_key]["options"][f"Выбор {j}"] = nxt
        else:
            # смерть
            dkey = f"D{i}_{j}"
            quest[scene_key]["options"][f"Выбор {j}"] = dkey
            quest[dkey] = {"text": death_line(), "options": {}}
            random_death_keys.append(dkey)

# Свяжем «реальные» ветки с автогенератором, чтобы игра была гигантской
quest["honest_pass"]["options"]["Резко изменить судьбу"] = "S1"
quest["career_now"]["options"]["Сменить трек"] = "S10"
quest["park_intro"]["options"]["Идти в неизвестность"] = "S25"
quest["home_intro"]["options"]["Выйти из дома и идти"] = "S50"
quest["job_search"]["options"]["Резкий поворот"] = "S75"
quest["uni_path"]["options"]["Случайное решение"] = "S100"

# Вероятности внезапных событий
RANDOM_EVENT_PROB = 0.10
SECRET_EVENT_PROB = 0.03
secret_list = list(secret_nodes.keys())


# =========================
# UI HELPERS
# =========================
def kb_options(options: dict | None) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    if not options:
        # в концовках показываем /restart и «Назад»
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


async def send_scene(user_id: int, message: Message):
    data = user_state[user_id]
    node = quest[data["scene"]]
    await message.answer(node["text"], reply_markup=kb_options(node.get("options")))


# =========================
# HANDLERS
# =========================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_state[message.from_user.id] = {"scene": "start", "history": []}
    await message.answer("🎮 Добро пожаловать. Любой финал — смерть. Удачи…")
    await send_scene(message.from_user.id, message)


@dp.message(Command("restart"))
async def cmd_restart(message: Message):
    user_state[message.from_user.id] = {"scene": "start", "history": []}
    await message.answer("🔄 Игра начата заново.")
    await send_scene(message.from_user.id, message)


@dp.message(Command("back"))
async def cmd_back(message: Message):
    data = user_state.get(message.from_user.id)
    if not data or not data["history"]:
        await message.answer("❌ Назад нельзя — вы в начале.")
        return
    data["scene"] = data["history"].pop()
    await message.answer("🔙 Шаг назад.")
    await send_scene(message.from_user.id, message)


@dp.message()
async def any_text(message: Message):
    uid = message.from_user.id
    data = user_state.get(uid)
    if not data:
        await message.answer("Напиши /start чтобы начать игру.")
        return

    # Кнопка «Назад»
    if message.text.strip() == "⬅️ Назад":
        await cmd_back(message)
        return

    current = quest[data["scene"]]
    options = current.get("options", {})

    if message.text not in options:
        await message.answer("Выбери один из вариантов на клавиатуре.")
        return

    # потенциальный форс-мажор/секрет — только если это не концовка
    next_key = options[message.text]

    if quest.get(next_key, {}).get("options", None):  # не концовка
        # секретная ветка с небольшим шансом
        if random.random() < SECRET_EVENT_PROB:
            next_key = random.choice(secret_list)
        # внезапная смерть (форс-мажор)
        elif random.random() < RANDOM_EVENT_PROB and random_death_keys:
            next_key = random.choice(random_death_keys)

    # записываем историю и двигаемся
    data["history"].append(data["scene"])
    data["scene"] = next_key
    await send_scene(uid, message)


# =========================
# RUN
# =========================
async def main():
    print("Бот запущен…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
