import os
import json
import requests
from typing import Any
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("899701970:AAFK3tzz3e909kjqAgXssu6")
BASE_URL = 'https://spo-13.mskobr.ru'
PAGE_PATH = '/uchashimsya/raspisanie-kanikuly'
KORPUS = 'Корпус Ярославский'
CACHE_FILE = 'cache_index.json'

def parse_schedule_files() -> list[dict[str, Any]]:
    response = requests.post(BASE_URL + '/v1/api/page/id', json={'path': PAGE_PATH})
    page_id = response.json()["data"]["id"]

    response = requests.get(BASE_URL + f'/v1/api/folder_and_file/list/{page_id}')
    folders = response.json()["data"]["folders"]

    schedule_folder = None
    for folder in folders:
        if 'расписание учебных' in folder["title"].lower():
            schedule_folder = folder
            break
    if schedule_folder is None:
        return []

    files = []
    for korpus in schedule_folder["folders"]:
        if korpus["title"] != KORPUS:
            continue
        for f in korpus["files"]:
            course = int(str(f["title"])[0])
            files.append({
                'file_id': int(f["id"]),
                'course': course,
                'src': str(f["src"]),
                'ext': str(f.get("ext", 'xlsx')),
                'url': BASE_URL + str(f["src"]),
            })
    return files

def is_new_file(file_id: int, src: str) -> bool:
    if not os.path.exists(CACHE_FILE):
        return True
    with open(CACHE_FILE, encoding='utf-8') as f:
        cache = json.load(f)
    return cache.get(str(file_id)) != src

def cache_file(file_id: int, course: int, src: str, url: str, ext: str) -> str:
    folder = f'c{course}'
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f'kurs{course}.{ext}')
    response = requests.get(url)
    with open(file_path, 'wb') as f:
        f.write(response.content)

    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding='utf-8') as f:
            cache = json.load(f)
    cache[str(file_id)] = src
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    return file_path

def check_updates() -> tuple[str, list[str]]:
    files = parse_schedule_files()
    lines = [f'Найдено файлов ({KORPUS}): {len(files)}']
    new_paths = []
    for f in files:
        if is_new_file(f['file_id'], f['src']):
            path = cache_file(f['file_id'], f['course'], f['src'], f['url'], f['ext'])
            lines.append(f'Скачан: {path}')
            new_paths.append(path)
        else:
            lines.append(f'Без изменений: c{f["course"]}/kurs{f["course"]}.{f["ext"]}')
    return '\n'.join(lines), new_paths

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Бот для расписания пар (Ярославский корпус).\n\n"
        "/update – проверить и скачать новые файлы\n"
        "/file <курс> – получить файл расписания для курса (1–4)\n"
        "/status – просто показывает, какие файлы есть в кэше"
    )

async def cmd_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Проверяю обновления...")
    report, new_files = check_updates()
    await msg.edit_text(report)
    for path in new_files:
        if os.path.exists(path):
            await update.message.reply_document(document=open(path, 'rb'))

async def cmd_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        course = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Укажи номер курса: /file 1")
        return
    if course not in (1, 2, 3, 4):
        await update.message.reply_text("Курс должен быть 1–4")
        return

    files = parse_schedule_files()
    ext = 'xlsx'
    for f in files:
        if f['course'] == course:
            ext = f['ext']
            break
    path = os.path.join(f'c{course}', f'kurs{course}.{ext}')
    if os.path.exists(path):
        await update.message.reply_document(document=open(path, 'rb'))
    else:
        await update.message.reply_text("Файл ещё не был скачан. Сделай /update")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(CACHE_FILE):
        await update.message.reply_text("Кэш пуст. Сделай /update")
        return
    with open(CACHE_FILE, encoding='utf-8') as f:
        cache = json.load(f)
    files = parse_schedule_files()
    lines = ["Записанные файлы:"]
    for f in files:
        status = "✔" if str(f['file_id']) in cache and cache[str(f['file_id'])] == f['src'] else "✘"
        lines.append(f"{status} Курс {f['course']} – c{f['course']}/kurs{f['course']}.{f['ext']}")
    await update.message.reply_text('\n'.join(lines))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("update", cmd_update))
    app.add_handler(CommandHandler("file", cmd_file))
    app.add_handler(CommandHandler("status", cmd_status))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()