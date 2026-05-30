import os
import json
import discord
from datetime import datetime
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Select
from dotenv import load_dotenv

# =========================
# Загрузка .env
# =========================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# ID канала для сообщений о сбросе
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
# SELECT СЕМЕЙ
# =========================
class FamilySelect(Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label=family
            )
            for family in FAMILIES
        ]

        super().__init__(
            placeholder="Выберите семью",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        selected_family = self.values[0]

        await interaction.response.edit_message(
            content=(
                f"👑 Выбрана семья: "
                f"**{selected_family}**\n\n"
                f"📍 Теперь выберите точку:"
            ),
            view=PointView(selected_family)
        )

# =========================
# SELECT ТОЧЕК
# =========================
class PointSelect(Select):

    def __init__(self, family_name):

        self.family_name = family_name

        points_data = load_points()

        options = []

        for point, owner in points_data.items():

            options.append(
                discord.SelectOption(
                    label=point,
                    description=f"Текущий владелец: {owner}"
                )
            )

        super().__init__(
            placeholder="Выберите точку влияния",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        selected_point = self.values[0]

        points_data = load_points()

        points_data[selected_point] = self.family_name

        save_points(points_data)

        embed = discord.Embed(
            title="📍 Обновление точки влияния",
            color=0x00ff99
        )

        embed.add_field(
            name="👑 Семья",
            value=self.family_name,
            inline=False
        )

        embed.add_field(
            name="📌 Точка",
            value=selected_point,
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )

# =========================
# VIEW СЕМЕЙ
# =========================
class FamilyView(View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            FamilySelect()
        )

# =========================
# VIEW ТОЧЕК
# =========================
class PointView(View):

    def __init__(self, family_name):

        super().__init__(timeout=None)

        self.add_item(
            PointSelect(family_name)
        )

# =========================
# /setfamily
# =========================
@tree.command(
    name="setfamily",
    description="Назначить семью"
)
async def setfamily(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "👑 Выберите семью:",
        view=FamilyView(),
        ephemeral=True
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

    try:
        synced = await tree.sync()

        print(
            f"✅ Synced {len(synced)} commands."
        )

    except Exception as e:
        print(f"❌ Ошибка sync: {e}")

    print(f"✅ Бот запущен как {bot.user}")

    if not reset_points.is_running():
        reset_points.start()

# =========================
# START
# =========================
bot.run(TOKEN)
