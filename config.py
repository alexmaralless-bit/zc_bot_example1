"""
Загрузка секретов из .env. Единственная причина этого слоя — не хардкодить
токен в main.py и не коммитить его в git.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не задан. Скопируй .env.example в .env и вставь токен от BotFather."
    )
