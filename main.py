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

# ID канала для логов сброса
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

# =========================
# Список семей
# =========================
FAMILIES = [
    "Reseller",
    "Giudice",
    "Demorgan",
    "Miamori",
    "Fruktik",
    "Obsidian",
    "Худричи",
    "Velmora"
]

# =========================
# Создание файла
# =========================
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
class SetFamilyModal(
    Modal,
    title="Назначение семьи"
):

    point = TextInput(
        label="Точка влияния",
        placeholder="Баржа / Притон / Лес...",
        required=True
    )

    family = TextInput(
        label="Семья",
        placeholder="Reseller / Giudice ...",
        required=True
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        points = load_points()

        point_name = self.point.value.strip()
        family_name = self.family.value.strip()

        # Проверка точки
        if point_name not in points:

            points_list = "\n".join(
                default_points.keys()
            )

            await interaction.response.send_message(
                f"❌ Такой точки нет.\n\n"
                f"Доступные точки:\n{points_list}",
                ephemeral=True
            )

            return

        # Проверка семьи
        if family_name not in FAMILIES:

            fam_list = "\n".join(FAMILIES)

            await interaction.response.send_message(
                f"❌ Такой семьи нет.\n\n"
                f"Доступные семьи:\n{fam_list}",
                ephemeral=True
            )

            return

        points[point_name] = family_name

        save_points(points)

        embed = discord.Embed(
            title="📍 Обновление точки влияния",
            color=0x00ff99
        )

        embed.add_field(
            name="📌 Точка",
            value=point_name,
            inline=False
        )

        embed.add_field(
            name="👑 Семья",
            value=family_name,
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )

# =========================
# /setfamily
# =========================
@tree.command(
    name="setfamily",
    description="Назначить семью на точку"
)
async def setfamily(
    interaction: discord.Interaction
):
    await interaction.response.send_modal(
        SetFamilyModal()
    )

# =========================
# /points
# =========================
@tree.command(
    name="points",
    description="Список точек влияния"
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
# /addfamily
# =========================
@tree.command(
    name="addfamily",
    description="Добавить семью"
)
@app_commands.describe(
    family="Название семьи"
)
async def addfamily(
    interaction: discord.Interaction,
    family: str
):

    if family in FAMILIES:

        await interaction.response.send_message(
            "❌ Семья уже существует.",
            ephemeral=True
        )

        return

    FAMILIES.append(family)

    await interaction.response.send_message(
        f"✅ Семья **{family}** добавлена."
    )

# =========================
# /removefamily
# =========================
@tree.command(
    name="removefamily",
    description="Удалить семью"
)
@app_commands.describe(
    family="Название семьи"
)
async def removefamily(
    interaction: discord.Interaction,
    family: str
):

    if family not in FAMILIES:

        await interaction.response.send_message(
            "❌ Семья не найдена.",
            ephemeral=True
        )

        return

    FAMILIES.remove(family)

    await interaction.response.send_message(
        f"✅ Семья **{family}** удалена."
    )

# =========================
# /families
# =========================
@tree.command(
    name="families",
    description="Список семей"
)
async def families(
    interaction: discord.Interaction
):

    fam_list = "\n".join(
        [f"• {fam}" for fam in FAMILIES]
    )

    embed = discord.Embed(
        title="👑 Список семей",
        description=fam_list,
        color=0xff9900
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
