
import os
import asyncio
import threading
from datetime import datetime

import discord
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SITE_SECRET = os.getenv("SITE_SECRET", "")
ANKETA_CHANNEL_ID = int(os.getenv("ANKETA_CHANNEL_ID", "0"))

app = Flask(__name__)

intents = discord.Intents.default()
bot = discord.Client(intents=intents)


# Поля анкеты — порядок и названия не менять
ANKETA_FIELDS = [
    ("Игровой ник:", "nickname"),
    ("Игровой уровень:", "level"),
    ("ID Аккаунта:", "account_id"),
    ("Возраст:", "age"),
    ("Имя:", "name"),
    ("Город:", "city"),
    ("Дискорд:", "discord"),
    ("Онлайн:", "online"),
    ("Ссылка форума:", "forum"),
    ("Ссылка вк:", "vk"),
    ("Ссылка на РП БИО:", "rp_bio"),
    ("Ссылка на личное дело:", "personal_file"),
    ("Причина постановления:", "reason"),
    ("Занимал ли высокие должности:", "high_position"),
    ("Привязан ли аккаунт к почте / гугл аутентификатору / ВК ЛК:", "linked"),
    (
        "Имеются ли твинки на 05 сервере и были ли на них баны ( Если да, то какие ):",
        "twinks",
    ),
    ("Должность, на которую будет поставлен:", "position"),
]


@app.route("/")
def website_status():
    return "Discord bot is online"


@app.route("/submit", methods=["POST", "OPTIONS"])
def submit_anketa():
    if request.method == "OPTIONS":
        return "", 204

    if not TOKEN:
        return jsonify({
            "success": False,
            "error": "DISCORD_TOKEN не настроен"
        }), 500

    if not SITE_SECRET:
        return jsonify({
            "success": False,
            "error": "SITE_SECRET не настроен"
        }), 500

    if request.headers.get("X-Site-Secret") != SITE_SECRET:
        return jsonify({
            "success": False,
            "error": "Неверный секрет"
        }), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Данные анкеты не получены"
        }), 400

    if ANKETA_CHANNEL_ID == 0:
        return jsonify({
            "success": False,
            "error": "ANKETA_CHANNEL_ID не настроен"
        }), 500

    if not bot.is_ready():
        return jsonify({
            "success": False,
            "error": "Discord-бот ещё запускается"
        }), 503

    try:
        future = asyncio.run_coroutine_threadsafe(
            send_anketa(data),
            bot.loop
        )
        future.result(timeout=20)

        return jsonify({
            "success": True,
            "message": "Анкета успешно отправлена"
        }), 200

    except Exception as error:
        app.logger.exception("Не удалось отправить анкету")

        return jsonify({
            "success": False,
            "error": "Не удалось отправить анкету в Discord"
        }), 500



async def send_anketa(data):
    channel = bot.get_channel(ANKETA_CHANNEL_ID)

    if channel is None:
        channel = await bot.fetch_channel(ANKETA_CHANNEL_ID)

    fields = [
        ("Игровой ник:", "nickname"),
        ("Игровой уровень:", "level"),
        ("ID Аккаунта:", "account_id"),
        ("Возраст:", "age"),
        ("Имя:", "name"),
        ("Город:", "city"),
        ("Дискорд:", "discord"),
        ("Онлайн:", "online"),
        ("Ссылка форума:", "forum"),
        ("Ссылка вк:", "vk"),
        ("Ссылка на РП БИО:", "rp_bio"),
        ("Ссылка на личное дело:", "personal_file"),
        ("Причина постановления:", "reason"),
        ("Занимал ли высокие должности:", "high_position"),
        ("Привязан ли аккаунт к почте / гугл аутентификатору / ВК ЛК:", "linked"),
        ("Имеются ли твинки на 05 сервере и были ли на них баны ( Если да, то какие ):",
         "twinks"),
        ("Должность, на которую будет поставлен:", "position"),
    ]

    lines = []

    for label, key in fields:
        value = data.get(key)

        if value is None or str(value).strip() == "":
            value = "Не указано"
        else:
            value = str(value).strip()

        lines.append(f"{label} {value}")

    message = "\n".join(lines)

    if len(message) <= 2000:
        await channel.send(message)
    else:
        parts = []
        current = ""

        for line in lines:
            addition = line + "\n"

            if len(current) + len(addition) > 1990:
                parts.append(current.rstrip())
                current = ""

            current += addition

        if current.strip():
            parts.append(current.rstrip())

        for part in parts:
            await channel.send(part)


def run_website():
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, threaded=True)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Не задана переменная DISCORD_TOKEN")

    website_thread = threading.Thread(
        target=run_website,
        daemon=True
    )
    website_thread.start()

    bot.run(TOKEN)
