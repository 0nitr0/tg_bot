import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Загружаем токен из переменных окружения Render
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ====== Логика сюжета ======
quest = {
    "start": {
        "text": "Ты подросток в школе. У тебя есть выбор: пойти учиться или прогулять.",
        "options": {
            "Учиться": "study_school",
            "Прогулять": "skip_school"
        }
    },
    "study_school": {
        "text": "Ты учился хорошо. У тебя появился шанс поступить в университет. Что выберешь?",
        "options": {
            "Поступить в универ": "university",
            "Пойти работать сразу": "work_early"
        }
    },
    "skip_school": {
        "text": "Ты прогуливал и плохо учился. Тебе тяжело найти нормальную работу. Что будешь делать?",
        "options": {
            "Пойти работать где получится": "hard_job",
            "Попробовать исправиться и доучиться": "study_late"
        }
    },
    "university": {
        "text": "В университете тебе нужно выбрать профессию. Кем станешь?",
        "options": {
            "Программист": "dev_path",
            "Врач": "doctor_path",
            "Художник": "artist_path"
        }
    },
    "work_early": {
        "text": "Ты пошёл работать на завод. Жизнь тяжёлая, но стабильная.",
        "options": {
            "Продолжить работать": "factory_life",
            "Попробовать учиться заочно": "evening_school"
        }
    },
    "dev_path": {
        "text": "Ты выбрал профессию программиста. Началась интересная, но стрессовая жизнь в IT.",
        "options": {
            "Стартап": "startup",
            "Работа в корпорации": "corporation"
        }
    },
    "doctor_path": {
        "text": "Ты стал врачом. Жизнь полна ответственности и вызовов.",
        "options": {
            "Работать в больнице": "hospital",
            "Открыть частную клинику": "private_clinic"
        }
    },
    "artist_path": {
        "text": "Ты стал художником. Жизнь полна творчества, но и нестабильности.",
        "options": {
            "Выставки": "exhibitions",
            "Работа на заказ": "commissions"
        }
    },
    "hard_job": {
        "text": "Ты работаешь разнорабочим. Тяжело, но даёт опыт.",
        "options": {
            "Продолжать": "ordinary_life",
            "Искать шанс": "chance_life"
        }
    },
    "study_late": {
        "text": "Ты решил исправиться и снова учиться. Это было сложно, но у тебя появился шанс на будущее.",
        "options": {
            "Поступить в колледж": "college",
            "Пойти в армию": "army"
        }
    },
    # Финалы
    "startup": {
        "text": "Ты основал стартап, рисковал — и добился успеха. Ты миллионер!",
        "options": {}
    },
    "corporation": {
        "text": "Ты работаешь в корпорации. Хорошая зарплата, но нет свободы.",
        "options": {}
    },
    "hospital": {
        "text": "Ты врач в больнице. Уважаемая и стабильная работа.",
        "options": {}
    },
    "private_clinic": {
        "text": "Ты открыл частную клинику и разбогател.",
        "options": {}
    },
    "exhibitions": {
        "text": "Ты стал известным художником, твои картины покупают в галереях.",
        "options": {}
    },
    "commissions": {
        "text": "Ты рисуешь на заказ. Доход небольшой, но душа спокойна.",
        "options": {}
    },
    "factory_life": {
        "text": "Ты всю жизнь проработал на заводе. У тебя стабильность, но без больших достижений.",
        "options": {}
    },
    "evening_school": {
        "text": "Ты закончил вечернюю школу и получил шанс сменить профессию.",
        "options": {
            "Пойти в универ": "university"
        }
    },
    "ordinary_life": {
        "text": "Ты прожил обычную жизнь без особых успехов.",
        "options": {}
    },
    "chance_life": {
        "text": "Ты рискнул, нашёл новые возможности и изменил свою жизнь к лучшему.",
        "options": {}
    },
    "college": {
        "text": "Ты закончил колледж и получил профессию.",
        "options": {}
    },
    "army": {
        "text": "Ты пошёл в армию. Это изменило твою жизнь.",
        "options": {}
    }
}

# ====== Клавиатура ======
def get_keyboard(options: dict):
    keyboard = [[KeyboardButton(text=option)] for option in options.keys()]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

# ====== Хендлеры ======
@dp.message(Command("start"))
async def start_game(message: types.Message):
    scene = quest["start"]
    await message.answer(scene["text"], reply_markup=get_keyboard(scene["options"]))

@dp.message()
async def play(message: types.Message):
    for scene_name, scene in quest.items():
        if message.text in scene.get("options", {}):
            next_scene = quest[scene["options"][message.text]]
            await message.answer(next_scene["text"], reply_markup=get_keyboard(next_scene.get("options", {})))
            return
    await message.answer("Я не понял твой выбор. Попробуй снова.")

# ====== Запуск ======
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
