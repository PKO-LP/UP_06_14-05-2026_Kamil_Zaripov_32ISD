# Автоматическая проверка — `parser.py`

_Проверено: 2026-06-14 19:44_

**Ошибок: 0** из 11 шагов

---

## OK — Верно выполненные шаги

- OK Шаг 1: `response.json()["data"]["id"]`
- OK Шаг 2: `response.json()["data"]["folders"]`
- OK Шаг 3: `folder["title"]`
- OK Шаг 4 (цикл корпусов): `schedule_folder["folders"]`
- OK Шаг 4 (сравнение корпуса): `korpus["title"] != KORPUS`
- OK Шаг 4 (цикл файлов): `korpus["files"]`
- OK Шаг 4 (course): `str(f["title"])[0]`
- OK Шаг 4 (file_id): `'file_id': int(f["id"])`
- OK Шаг 4 (src): `'src': str(f["src"])`
- OK Шаг 4 (ext): `f.get("ext",`
- OK Шаг 4 (url): `BASE_URL + str(f["src"])`

---
<!-- BOT_CHECK_START -->
## 🤖 Проверка Telegram-бота

| Проверка | Результат |
|----------|-----------|
| 📁 Бот-файл найден | ✅ |
| 📋 requirements.txt | ❌ |
| 📦 TG-библиотека в requirements | ❌ |
| ▶️  Обработчик /start | ✅ |
| 🛡️  .gitignore содержит .env | ❌ |
| 🔑 Токен не в коде | ✅ |
| 🔐 Переменные окружения | ✅ |

| Этап | Статус |
|------|--------|
| 🚀 Этап 1 — Бот запущен | ✅ Реализовано |
| 📅 Этап 2 — Расписание | ✅ Реализовано |
| 💾 Этап 3 — Кеширование | ✅ Реализовано |
<!-- BOT_CHECK_END -->