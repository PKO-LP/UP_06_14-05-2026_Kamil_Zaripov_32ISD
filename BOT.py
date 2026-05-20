import os
import json
import asyncio
import logging

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties



load_dotenv()

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("TOKEN не найден")



bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()



CACHE_FILE = "cache_index.json"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

cache = load_cache()


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Расписание",
                    callback_data="schedule"
                ),
                InlineKeyboardButton(
                    text="🔄 Обновить",
                    callback_data="refresh"
                )
            ]
        ]
    )


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет!\nВыбери действие:",
        reply_markup=main_menu()
    )



def get_schedule_files():
    files = []

    for folder in os.listdir("."):
        if not folder.startswith("c"):
            continue

        if not os.path.isdir(folder):
            continue

        for file in os.listdir(folder):
            if not file.endswith((".xlsx", ".xls")):
                continue

            path = os.path.join(folder, file)

            file_id = f"{folder}_{file}"
            mtime = os.path.getmtime(path)

            files.append({
                "file_id": file_id,
                "course": folder.replace("c", ""),
                "path": path,
                "mtime": mtime,
                "ext": file.split(".")[-1]
            })

    return files



@dp.callback_query(F.data == "schedule")
async def schedule_handler(call: CallbackQuery):

    await call.message.answer("Загружаю расписание...")

    files = get_schedule_files()

    if not files:
        await call.message.answer("❌ Нет файлов в папках c1, c2, c3...")
        return

    for f in files:

        try:
            is_new = (
                f["file_id"] not in cache
                or cache[f["file_id"]] != f["mtime"]
            )

            document = FSInputFile(f["path"])

            if is_new:
                await call.message.answer_document(
                    document,
                    caption="🆕 Новое расписание"
                )
                cache[f["file_id"]] = f["mtime"]
            else:
                await call.message.answer_document(
                    document,
                    caption="Без изменений"
                )

        except Exception as e:
            print("Ошибка файла:", e)

    save_cache(cache)


@dp.callback_query(F.data == "refresh")
async def refresh_handler(call: CallbackQuery):

    await call.message.answer("🔄 Обновлено")
    await call.message.answer(
        "Выбери действие:",
        reply_markup=main_menu()
    )


async def main():

    logging.basicConfig(level=logging.INFO)

    await bot.delete_webhook(drop_pending_updates=True)

    print("Бот запущен (без Cloudflare Worker)")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
