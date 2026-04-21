"""
Слой данных. Отвечает только за SQLite: создать таблицу, положить задачу,
вернуть список. Никаких тг-штук здесь нет — модуль можно переиспользовать
хоть из CLI, хоть из веба.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / "tasks.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Создаёт таблицу `tasks`, если её ещё нет."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                text        TEXT NOT NULL,
                user        TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
            """
        )


def add_task(text: str, user: str) -> int:
    """Сохраняет новую задачу. Возвращает id вставленной строки."""
    created_at = datetime.now().isoformat(timespec="seconds")
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (text, user, created_at) VALUES (?, ?, ?)",
            (text, user, created_at),
        )
        return cur.lastrowid


def list_tasks() -> list[dict]:
    """Возвращает все задачи в порядке добавления."""
    with _connect() as conn:
        cur = conn.execute(
            "SELECT id, text, user, created_at FROM tasks ORDER BY id"
        )
        return [dict(row) for row in cur.fetchall()]
