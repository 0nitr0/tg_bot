# bot.py — aiogram 3.x + Flask keep-alive for Render (ручные ветки, детерминированно)
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

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN", "PASTE_YOUR_TOKEN_HERE")
PORT = int(os.getenv("PORT", "8080"))
if not TOKEN or TOKEN == "PASTE_YOUR_TOKEN_HERE":
    print("⚠️ Установи переменную окружения TELEGRAM_TOKEN.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Flask keep-alive (Render) ---
app = Flask(__name__)
@app.route("/")
def index():
    return "Бот работает! 💡"
def run_web():
    app.run(host="0.0.0.0", port=PORT)
threading.Thread(target=run_web, daemon=True).start()

# ========= ВСПОМОГАТЕЛЬНОЕ =========
user_state: dict[int, dict] = {}  # {user_id: {"scene": str, "history": [str,...]}}

def ending(text: str) -> str:
    return f"{text}\n\n/restart - начать заново"

def kb(options: dict | None):
    if not options:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="/restart")],
                [KeyboardButton(text="⬅️ Назад")],
            ],
            resize_keyboard=True,
        )
    rows = [[KeyboardButton(text=o)] for o in options.keys()]
    rows.append([KeyboardButton(text="⬅️ Назад")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

async def send_scene(uid: int, msg: Message):
    node = quest[user_state[uid]["scene"]]
    await msg.answer(node["text"], reply_markup=kb(node.get("options")))

# ========= СЮЖЕТ (РУЧНОЙ) =========
# Все ветки прописаны руками. Хотите больше — копируйте и расширяйте блоки.
quest: dict[str, dict] = {
    # Стартовый хаб
    "start": {
        "text": "Ты просыпаешься в обычный день. Куда направишься?",
        "options": {
            "🎓 Школа": "SCH_INTRO",
            "🏠 Дом": "HOME_INTRO",
            "🌆 Город": "CITY_INTRO",
            "💼 Карьера": "CAR_INTRO",
        }
    },

    # ==== ШКОЛА ====
    "SCH_INTRO": {
        "text": "Школьный коридор, звонок близко. С чего начнёшь?",
        "options": {
            "Тест по математике": "SCH_MATH",
            "Классный час": "SCH_HRM",
            "Олимпиада": "SCH_OLY",
        }
    },
    "SCH_MATH": {
        "text": "Лист с заданиями перед тобой. Как действуешь?",
        "options": {
            "Списывать у соседа": "END_SCH_1",
            "Честно решать": "SCH_MATH_HON",
            "Сдать пустой лист": "END_SCH_2",
        }
    },
    "SCH_MATH_HON": {
        "text": "Время на исходе, решение почти готово...",
        "options": {
            "Сдать вовремя": "END_SCH_3",
            "Паниковать и переписывать": "END_SCH_4",
            "Попросить подсказку у учителя": "END_SCH_5",
        }
    },
    "SCH_HRM": {
        "text": "Учитель поднимает неприятную тему. Твои действия?",
        "options": {
            "Поспорить с учителем": "END_SCH_6",
            "Защитить одноклассника": "END_SCH_7",
            "Промолчать": "END_SCH_8",
        }
    },
    "SCH_OLY": {
        "text": "Запись на олимпиаду. Что выбираешь?",
        "options": {
            "Теоретический тур": "END_SCH_9",
            "Практический тур": "END_SCH_10",
            "Вообще не идти": "END_SCH_11",
        }
    },

    # ==== ДОМ ====
    "HOME_INTRO": {
        "text": "Тихий коридор квартиры. Чем займёшься?",
        "options": {
            "Позвонить бабушке": "HOME_GRAND",
            "Сидеть в интернете": "HOME_NET",
            "Разобраться с шумными соседями": "HOME_NEIB",
        }
    },
    "HOME_GRAND": {
        "text": "Бабушка рада звонку. Что дальше?",
        "options": {
            "Пойти в гости": "END_HOME_1",
            "Отложить звонок": "END_HOME_2",
            "Попросить рецепт пирога": "END_HOME_3",
        }
    },
    "HOME_NET": {
        "text": "Открыт браузер. Решайся.",
        "options": {
            "Скачать пиратку": "END_HOME_4",
            "Заказать еду и сериал": "END_HOME_5",
            "Лечь спать": "END_HOME_6",
        }
    },
    "HOME_NEIB": {
        "text": "На площадке слышны крики. Что сделаешь?",
        "options": {
            "Разнять драку": "END_HOME_7",
            "Вызвать полицию": "END_HOME_8",
            "Игнорировать": "END_HOME_9",
        }
    },

    # ==== ГОРОД ====
    "CITY_INTRO": {
        "text": "Серый город, шум машин. Куда свернёшь?",
        "options": {
            "Метро": "CITY_METRO",
            "Бандиты во дворе": "CITY_GANG",
            "Заброшенное здание": "CITY_RUIN",
        }
    },
    "CITY_METRO": {
        "text": "Поезд уходит. Твой ход?",
        "options": {
            "Запрыгнуть в закрывающиеся двери": "END_CITY_1",
            "Ждать следующий поезд": "END_CITY_2",
            "Спуститься на пути (опасно!)": "END_CITY_3",
        }
    },
    "CITY_GANG": {
        "text": "Трое подозрительных парней приближаются...",
        "options": {
            "Отдать кошелёк": "END_CITY_4",
            "Сопротивляться": "END_CITY_5",
            "Бежать": "END_CITY_6",
        }
    },
    "CITY_RUIN": {
        "text": "Заброшка манит темнотой. Что делаем?",
        "options": {
            "Зайти внутрь": "END_CITY_7",
            "Сфотографировать и уйти": "END_CITY_8",
            "Искать вход в подвал": "END_CITY_9",
        }
    },

    # ==== КАРЬЕРА ====
    "CAR_INTRO": {
        "text": "Кабинеты, дедлайны, переговорки. С чего начнёшь?",
        "options": {
            "Собеседование": "CAR_INT",
            "Стартап": "CAR_ST",
            "Офисные интриги": "CAR_POL",
        }
    },
    "CAR_INT": {
        "text": "HR улыбается, но смотрит пристально...",
        "options": {
            "Приукрасить резюме": "END_CAR_1",
            "Говорить только правду": "END_CAR_2",
            "Сделать тестовое задание": "END_CAR_3",
        }
    },
    "CAR_ST": {
        "text": "Идея кажется гениальной. Как финансировать?",
        "options": {
            "Взять кредит": "END_CAR_4",
            "Без инвестиций, на свои": "END_CAR_5",
            "Продать долю партнёру": "END_CAR_6",
        }
    },
    "CAR_POL": {
        "text": "Коллега косячит и кивает на тебя...",
        "options": {
            "Сдать коллегу": "END_CAR_7",
            "Взять вину на себя": "END_CAR_8",
            "Ничего не делать": "END_CAR_9",
        }
    },

    # ==== КОНЦОВКИ (ВСЕ — СМЕРТИ) ====
    # ШКОЛА (11)
    "END_SCH_1": {"text": ending("Тебя поймали на списывании. Позор пережить не удалось.") , "options": {}},
    "END_SCH_2": {"text": ending("Пустой лист — пустое будущее. Твоя история оборвалась.") , "options": {}},
    "END_SCH_3": {"text": ending("Сдал вовремя — но сердце не выдержало напряжения.") , "options": {}},
    "END_SCH_4": {"text": ending("Паника лишила сил. Последний звонок прозвучал для тебя.") , "options": {}},
    "END_SCH_5": {"text": ending("Учитель не простил подсказок. Судьба оборвалась.") , "options": {}},
    "END_SCH_6": {"text": ending("Спор перерос в конфликт. Точка.") , "options": {}},
    "END_SCH_7": {"text": ending("Защищая друга, ты пал героем школьного фронта.") , "options": {}},
    "END_SCH_8": {"text": ending("Молчание стало приговором. Свет погас.") , "options": {}},
    "END_SCH_9": {"text": ending("Теория поглотила тебя навсегда.") , "options": {}},
    "END_SCH_10":{"text": ending("Практика оказалась смертельно опасной.") , "options": {}},
    "END_SCH_11":{"text": ending("Шанс упущен. Время тоже.") , "options": {}},

    # ДОМ (9)
    "END_HOME_1": {"text": ending("Дорога в гости стала последней.") , "options": {}},
    "END_HOME_2": {"text": ending("Отложенный звонок отложил и твою судьбу — навсегда.") , "options": {}},
    "END_HOME_3": {"text": ending("Пирог удался... но нет.") , "options": {}},
    "END_HOME_4": {"text": ending("Пиратка принесла не только вирусы, но и финал.") , "options": {}},
    "END_HOME_5": {"text": ending("Еда, сериал, вечность. Экран погас вместе с тобой.") , "options": {}},
    "END_HOME_6": {"text": ending("Сон оказался вечным.") , "options": {}},
    "END_HOME_7": {"text": ending("Разнять драку — рискованный выбор. Последний.") , "options": {}},
    "END_HOME_8": {"text": ending("Полиция приехала слишком поздно и для тебя тоже.") , "options": {}},
    "END_HOME_9": {"text": ending("Игнорируя чужую беду, ты проигнорировал и свою судьбу.") , "options": {}},

    # ГОРОД (9)
    "END_CITY_1": {"text": ending("Двери метро закрылись навсегда.") , "options": {}},
    "END_CITY_2": {"text": ending("Ожидание затянулось до конца времён.") , "options": {}},
    "END_CITY_3": {"text": ending("Рельсы не прощают ошибок.") , "options": {}},
    "END_CITY_4": {"text": ending("Кошелёк ушёл, а за ним и жизнь.") , "options": {}},
    "END_CITY_5": {"text": ending("Сопротивление оказалось последним.") , "options": {}},
    "END_CITY_6": {"text": ending("Не убежал. Не успел.") , "options": {}},
    "END_CITY_7": {"text": ending("Заброшка хранила слишком много тайн.") , "options": {}},
    "END_CITY_8": {"text": ending("Снимок получился удачным. Последним.") , "options": {}},
    "END_CITY_9": {"text": ending("Подвал принял тебя без возврата.") , "options": {}},

    # КАРЬЕРА (9)
    "END_CAR_1": {"text": ending("Ложь в резюме стоила слишком дорого.") , "options": {}},
    "END_CAR_2": {"text": ending("Правда освобождает, но не тебя.") , "options": {}},
    "END_CAR_3": {"text": ending("Тестовое задание оказалось смертельным квестом.") , "options": {}},
    "END_CAR_4": {"text": ending("Кредит оказался последним решением.") , "options": {}},
    "END_CAR_5": {"text": ending("Без денег — без шансов. И без продолжения.") , "options": {}},
    "END_CAR_6": {"text": ending("Долю продал, себя — тоже.") , "options": {}},
    "END_CAR_7": {"text": ending("Интриги похоронили всех, включая тебя.") , "options": {}},
    "END_CAR_8": {"text": ending("Благородный поступок стал последним.") , "options": {}},
    "END_CAR_9": {"text": ending("Пассивность — тоже выбор. Финальный.") , "options": {}},
}

# ========= ВАЛИДАЦИЯ (опционально, но полезно) =========
def validate_story():
    errors = []
    total_endings = 0
    for k, v in quest.items():
        opts = v.get("options", {})
        if not opts:
            total_endings += 1
        else:
            for label, target in opts.items():
                if target not in quest:
                    errors.append(f"{k} -> '{label}' -> отсутствует сцена '{target}'")
    if errors:
        print("❌ Ошибки ссылок в сюжете:")
        for e in errors:
            print("  -", e)
    else:
        print(f"✅ Сюжет валиден. Концовок: {total_endings}")

# ========= ХЭНДЛЕРЫ =========
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
    node = quest[data["scene"]]
    options = node.get("options", {})
    txt = (message.text or "").strip()

    if txt == "/restart":
        await cmd_start(message)
        return

    if txt not in options:
        await message.answer("Выбери один из вариантов на клавиатуре.")
        return

    data["history"].append(data["scene"])
    data["scene"] = options[txt]
    await send_scene(uid, message)

# ========= ЗАПУСК =========
async def main():
    validate_story()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
