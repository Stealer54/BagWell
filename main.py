import os
import json
import discord
from datetime import datetime
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Modal, TextInput
from dotenv import load_dotenv

# =========================
# Загрузка .env
# =========================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# ID канала для логов
POINTS_CHANNEL_ID = 123456789012345678

# =========================
# Discord настройки
# =========================
intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

tree = bot.tree

# =========================
# points.json
# =========================
DATA_FILE = "points.json"

default_points = {
    "Баржа": "Свободно",
    "Старые Фибы (Noose)": "Свободно",
    "Притон": "Свободно",
    "ЛНС (каменоломня)": "Свободно",
    "Лес (лесопилка)": "Свободно",
    "Лабиринт (Kortz)": "Свободно"
}

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(default_points, f, ensure_ascii=False, indent=4)

# =========================
# Загрузка данных
# =========================
def load_points():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# Сохранение данных
# =========================
def save_points(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# =========================
# МОДАЛКА
# =========================
class PointModal(Modal, title="Точки влияния"):

    family = TextInput(
        label="Название семьи",
        placeholder="Введите название семьи",
        required=True
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        points = load_points()

        # Пример:
        # автоматически занимает первую свободную точку
        free_point = None

        for point, owner in points.items():
            if owner == "Свободно":
                free_point = point
                break

        if free_point is None:
            await interaction.response.send_message(
                "❌ Свободных точек нет.",
                ephemeral=True
            )
            return

        points[free_point] = self.family.value

        save_points(points)

        embed = discord.Embed(
            title="📍 Точки влияния",
            description=(
                f"👑 Семья: **{self.family.value}**\n"
                f"📌 Захватила: **{free_point}**"
            ),
            color=0xff9900
        )

        await interaction.response.send_message(
            embed=embed
        )

# =========================
# КОМАНДА
# =========================
@tree.command(
    name="capture",
    description="Захватить точку"
)
async def capture(
    interaction: discord.Interaction
):
    await interaction.response.send_modal(
        PointModal()
    )

# =========================
# КОМАНДА СПИСКА
# =========================
@tree.command(
    name="points",
    description="Список точек"
)
async def points(
    interaction: discord.Interaction
):
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
# АВТОСБРОС
# =========================
@tasks.loop(minutes=1)
async def reset_points():

    now = datetime.now()

    # четверг и воскресенье
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
                title="🔄 Сброс точек влияния",
                description="Все точки были очищены.",
                color=0xff0000
            )

            await channel.send(embed=embed)

# =========================
# READY
# =========================
@bot.event
async def on_ready():

    await tree.sync()

    print(f"✅ Бот запущен как {bot.user}")

    if not reset_points.is_running():
        reset_points.start()

# =========================
# START
# =========================
bot.run(TOKEN)
