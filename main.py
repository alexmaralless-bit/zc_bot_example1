"""
Точка входа. Поднимает aiogram 3.x, регистрирует хэндлеры команд и начинает
long-polling. Бизнес-логика живёт в database.py.

Команды бота:
    /start      — приветствие, список команд
    /add <текст>— добавить задачу
    /list       — вывести все задачи в чат
    /list_csv   — сформировать CSV и прислать файлом
"""

import asyncio
import csv
import io
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, Message

from config import BOT_TOKEN
from database import add_task, init_db, list_tasks

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()


def _user_label(message: Message) -> str:
    """Красивая метка пользователя для поля `user` в БД."""
    u = message.from_user
    if u is None:
        return "unknown"
    return f"@{u.username}" if u.username else f"id:{u.id}"


@dp.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот-менеджер задач.\n\n"
        "Команды:\n"
        "  /add <текст> — добавить задачу\n"
        "  /list — показать все задачи\n"
        "  /list_csv — выгрузить задачи в CSV"
    )


@dp.message(Command("add"))
async def on_add(message: Message) -> None:
    # всё после "/add " считаем текстом задачи
    text = (message.text or "").removeprefix("/add").strip()
    if not text:
        await message.answer("Укажи текст задачи, например:\n`/add купить молоко`", parse_mode="Markdown")
        return
    task_id = add_task(text=text, user=_user_label(message))
    await message.answer(f"✅ Добавлено #{task_id}: {text}")


@dp.message(Command("list"))
async def on_list(message: Message) -> None:
    tasks = list_tasks()
    if not tasks:
        await message.answer("📭 Задач пока нет. Добавь первую: `/add ...`", parse_mode="Markdown")
        return
    lines = [
        f"{t['id']}. {t['text']}  —  {t['user']}  ({t['created_at']})"
        for t in tasks
    ]
    await message.answer("\n".join(lines))


@dp.message(Command("list_csv"))
async def on_list_csv(message: Message) -> None:
    tasks = list_tasks()
    if not tasks:
        await message.answer("📭 Нечего выгружать — задач нет.")
        return

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["id", "text", "user", "created_at"])
    writer.writeheader()
    for t in tasks:
        writer.writerow(t)
    # utf-8-sig = UTF-8 с BOM, чтобы Excel открыл кириллицу корректно
    data = buf.getvalue().encode("utf-8-sig")
    file = BufferedInputFile(data, filename="tasks.csv")
    await message.answer_document(file, caption=f"📎 Задач: {len(tasks)}")


async def main() -> None:
    init_db()
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
