import os
import json
import discord
from datetime import datetime
from discord.ext import commands, tasks
from discord import app_commands, Interaction
from dotenv import load_dotenv

# =========================
# Загрузка .env
# =========================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# ID канала для сообщений о сбросе точек
POINTS_CHANNEL_ID = 1384641223779684504

# =========================
# Discord настройки
# =========================
intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# =========================
# ФАЙЛ С ТОЧКАМИ
# =========================
DATA_FILE = "points.json"

# =========================
# Точки влияния
# =========================
default_points = {
    "Баржа": "Свободно",
    "Старые Фибы (Noose)": "Свободно",
    "Притон": "Свободно",
    "ЛНС (каменоломня)": "Свободно",
    "Лес (лесопилка)": "Свободно",
    "Лабиринт (Kortz)": "Свободно"
}

# Создание файла points.json
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(default_points, f, ensure_ascii=False, indent=4)

# =========================
# Загрузка точек
# =========================
def load_points():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# Сохранение точек
# =========================
def save_points(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# =========================
# Команда /setfamily
# =========================
@tree.command(
    name="setfamily",
    description="Назначить семью на точку"
)
@app_commands.describe(
    point="Название точки",
    family="Название семьи"
)
async def setfamily(
    interaction: Interaction,
    point: str,
    family: str
):
    points = load_points()

    if point not in points:
        await interaction.response.send_message(
            "❌ Такой точки нет.",
            ephemeral=True
        )
        return

    points[point] = family

    save_points(points)

    await interaction.response.send_message(
        f"✅ Семья **{family}** удерживает **{point}**"
    )

# =========================
# Команда /points
# =========================
@tree.command(
    name="points",
    description="Список точек влияния"
)
async def points(interaction: Interaction):
    points_data = load_points()

    embed = discord.Embed(
        title="📍 Удержание точек влияния",
        color=0x00ff99
    )

    for point, family in points_data.items():
        embed.add_field(
            name=point,
            value=f"👑 {family}",
            inline=False
        )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# Автосброс точек
# =========================
@tasks.loop(minutes=1)
async def reset_points():
    now = datetime.now()

    # 3 = четверг
    # 6 = воскресенье
    if (
        now.weekday() in [3, 6]
        and now.hour == 0
        and now.minute == 0
    ):
        save_points(default_points)

        channel = bot.get_channel(
            POINTS_CHANNEL_ID
        )

        if channel:
            embed = discord.Embed(
                title="🔄 Обновление точек влияния",
                description="Все точки были сброшены.",
                color=0xff0000
            )

            await channel.send(embed=embed)

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    try:
        synced = await tree.sync()

        print(
            f"✅ Synced {len(synced)} slash commands."
        )

    except Exception as e:
        print(f"❌ Ошибка sync: {e}")

    print(f"🔗 Logged in as {bot.user}")

    if not reset_points.is_running():
        reset_points.start()

# =========================
# START BOT
# =========================
bot.run(TOKEN)
