import os
import json
import discord

from datetime import datetime, timedelta

from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Select

from dotenv import load_dotenv

# =====================================================
# Загрузка .env
# =====================================================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# =====================================================
# Discord настройки
# =====================================================
intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

tree = bot.tree

# =====================================================
# Файлы
# =====================================================
DATA_FILE = "points.json"

POINTS_MESSAGE_FILE = "points_message.json"

FAMILIES_MESSAGE_FILE = "families_message.json"

ISLAND_FILE = "island.json"

ISLAND_MESSAGE_FILE = "island_message.json"

# =====================================================
# Точки влияния
# =====================================================
default_points = {
    "Баржа": "Свободно",
    "Старые Фибы (Noose)": "Свободно",
    "Притон": "Свободно",
    "ЛНС (каменоломня)": "Свободно",
    "Лес (лесопилка)": "Свободно",
    "Лабиринт (Kortz)": "Свободно"
}

# =====================================================
# ПУЛ ОСТРОВА
# =====================================================
FAMILIES = [
    "Obsidian",
    "Худричи",
    "Reseller",
    "Demorgan",
    "Giudice",
    "Velmora",
    "Fruktik"
]

# =====================================================
# Создание points.json
# =====================================================
if not os.path.exists(DATA_FILE):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            default_points,
            f,
            ensure_ascii=False,
            indent=4
        )

# =====================================================
# Создание island.json
# =====================================================
if not os.path.exists(ISLAND_FILE):

    island_data = {
        "rotation_index": 0,

        "Четверг": {
            "date": "Не назначено",
            "places": {
                "1 место": FAMILIES[0],
                "2 место": FAMILIES[1],
                "3 место": FAMILIES[2]
            }
        },

        "Воскресение": {
            "date": "Не назначено",
            "places": {
                "1 место": FAMILIES[1],
                "2 место": FAMILIES[2],
                "3 место": FAMILIES[3]
            }
        }
    }

    with open(
        ISLAND_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            island_data,
            f,
            ensure_ascii=False,
            indent=4
        )

# =====================================================
# Загрузка points
# =====================================================
def load_points():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# =====================================================
# Сохранение points
# =====================================================
def save_points(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

# =====================================================
# Загрузка island
# =====================================================
def load_island():

    with open(
        ISLAND_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# =====================================================
# Сохранение island
# =====================================================
def save_island(data):

    with open(
        ISLAND_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

# =====================================================
# Embed points
# =====================================================
def create_points_embed():

    points_data = load_points()

    embed = discord.Embed(
        title="📍 Удержание точек влияния",
        color=0x2b2d31
    )

    for point, family in points_data.items():

        embed.add_field(
            name=point,
            value=f"👑 {family}",
            inline=False
        )

    return embed

# =====================================================
# Embed island
# =====================================================
def create_island_embed():

    data = load_island()

    embed = discord.Embed(
        title="🏝️ Удержание острова",
        color=0x2b2d31
    )

    for day in ["Четверг", "Воскресение"]:

        info = data[day]

        text = ""

        text += (
            f"📅 Дата: "
            f"**{info['date']}**\n\n"
        )

        for place, family in info["places"].items():

            text += (
                f"**{place}** — 👑 {family}\n"
            )

        embed.add_field(
            name=day,
            value=text,
            inline=False
        )

    return embed

# =====================================================
# Ротация острова
# =====================================================
def rotate_island():

    data = load_island()

    index = data["rotation_index"]

    # =================================================
    # Следующая ротация
    # =================================================
    index += 1

    if index >= len(FAMILIES):

        index = 0

    # =================================================
    # Четверг
    # =================================================
    thursday = []

    for i in range(3):

        family_index = (
            index + i
        ) % len(FAMILIES)

        thursday.append(
            FAMILIES[family_index]
        )

    # =================================================
    # Воскресение
    # =================================================
    sunday = []

    for i in range(1, 4):

        family_index = (
            index + i
        ) % len(FAMILIES)

        sunday.append(
            FAMILIES[family_index]
        )

    # =================================================
    # Даты
    # =================================================
    today = datetime.utcnow()

    days_until_thursday = (
        3 - today.weekday()
    ) % 7

    if days_until_thursday == 0:

        days_until_thursday = 7

    next_thursday = (
        today + timedelta(
            days=days_until_thursday
        )
    )

    days_until_sunday = (
        6 - today.weekday()
    ) % 7

    if days_until_sunday == 0:

        days_until_sunday = 7

    next_sunday = (
        today + timedelta(
            days=days_until_sunday
        )
    )

    # =================================================
    # Обновление данных
    # =================================================
    data["rotation_index"] = index

    data["Четверг"] = {
        "date": next_thursday.strftime(
            "%d.%m.%Y"
        ),
        "places": {
            "1 место": thursday[0],
            "2 место": thursday[1],
            "3 место": thursday[2]
        }
    }

    data["Воскресение"] = {
        "date": next_sunday.strftime(
            "%d.%m.%Y"
        ),
        "places": {
            "1 место": sunday[0],
            "2 место": sunday[1],
            "3 место": sunday[2]
        }
    }

    save_island(data)

# =====================================================
# Сохранение сообщений
# =====================================================
def save_message(
    file_name,
    channel_id,
    message_id
):

    data = {
        "channel_id": channel_id,
        "message_id": message_id
    }

    with open(
        file_name,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(data, f)

# =====================================================
# Загрузка сообщений
# =====================================================
def load_message(file_name):

    if not os.path.exists(file_name):

        return None

    with open(
        file_name,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# =====================================================
# Автообновление сообщений
# =====================================================
async def update_message(
    file_name,
    embed
):

    data = load_message(file_name)

    if not data:

        return

    try:

        channel = bot.get_channel(
            data["channel_id"]
        )

        message = await channel.fetch_message(
            data["message_id"]
        )

        await message.edit(
            embed=embed
        )

    except:

        pass

# =====================================================
# SELECT СЕМЕЙ
# =====================================================
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
            embed=None,
            view=PointView(selected_family)
        )

# =====================================================
# SELECT ТОЧЕК
# =====================================================
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
            placeholder="Выберите точку",
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

        await update_message(
            POINTS_MESSAGE_FILE,
            create_points_embed()
        )

        embed = discord.Embed(
            title="✅ Точка обновлена",
            color=0x00ff99
        )

        embed.add_field(
            name="📌 Точка",
            value=selected_point,
            inline=False
        )

        embed.add_field(
            name="👑 Семья",
            value=self.family_name,
            inline=False
        )

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

# =====================================================
# VIEW
# =====================================================
class FamilyView(View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            FamilySelect()
        )

class PointView(View):

    def __init__(self, family_name):

        super().__init__(timeout=None)

        self.add_item(
            PointSelect(family_name)
        )

# =====================================================
# /points
# =====================================================
@tree.command(
    name="points",
    description="Список точек"
)
async def points(
    interaction: discord.Interaction
):

    embed = create_points_embed()

    await interaction.response.send_message(
        embed=embed
    )

    message = await interaction.original_response()

    save_message(
        POINTS_MESSAGE_FILE,
        interaction.channel.id,
        message.id
    )

# =====================================================
# /island
# =====================================================
@tree.command(
    name="island",
    description="Список острова"
)
async def island(
    interaction: discord.Interaction
):

    embed = create_island_embed()

    await interaction.response.send_message(
        embed=embed
    )

    message = await interaction.original_response()

    save_message(
        ISLAND_MESSAGE_FILE,
        interaction.channel.id,
        message.id
    )

# =====================================================
# /setfamily
# =====================================================
@tree.command(
    name="setfamily",
    description="Назначить семью"
)
async def setfamily(
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="👑 Выберите семью",
        color=0x2b2d31
    )

    await interaction.response.send_message(
        embed=embed,
        view=FamilyView(),
        ephemeral=True
    )

# =====================================================
# /setisland
# =====================================================
@tree.command(
    name="setisland",
    description="Назначить семью на остров"
)
async def setisland(
    interaction: discord.Interaction,
    day: str,
    place: str,
    family: str
):

    data = load_island()

    data[day]["places"][place] = family

    save_island(data)

    await update_message(
        ISLAND_MESSAGE_FILE,
        create_island_embed()
    )

    embed = discord.Embed(
        title="✅ Остров обновлен",
        color=0x00ff99
    )

    embed.add_field(
        name="📅 День",
        value=day,
        inline=False
    )

    embed.add_field(
        name="🏆 Место",
        value=place,
        inline=False
    )

    embed.add_field(
        name="👑 Семья",
        value=family,
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

# =====================================================
# /clear
# =====================================================
@tree.command(
    name="clear",
    description="Удалить сообщения"
)
async def clear(
    interaction: discord.Interaction,
    amount: int
):

    if not interaction.user.guild_permissions.manage_messages:

        await interaction.response.send_message(
            "❌ Нет прав.",
            ephemeral=True
        )

        return

    await interaction.response.defer(
        ephemeral=True
    )

    deleted = await interaction.channel.purge(
        limit=amount
    )

    embed = discord.Embed(
        title="🗑️ Сообщения удалены",
        description=f"Удалено: **{len(deleted)}**",
        color=0xff0000
    )

    await interaction.followup.send(
        embed=embed,
        ephemeral=True
    )

# =====================================================
# Автообновление острова
# =====================================================
@tasks.loop(hours=1)
async def island_rotation_task():

    now = datetime.utcnow()

    weekday = now.weekday()

    hour = now.hour

    if (
        weekday in [3, 6]
        and hour == 0
    ):

        rotate_island()

        await update_message(
            ISLAND_MESSAGE_FILE,
            create_island_embed()
        )

# =====================================================
# READY
# =====================================================
@bot.event
async def on_ready():

    if not island_rotation_task.is_running():

        island_rotation_task.start()

    try:

        synced = await tree.sync()

        print(
            f"✅ Synced {len(synced)} commands."
        )

    except Exception as e:

        print(
            f"❌ Ошибка sync: {e}"
        )

    print(
        f"✅ Бот запущен как {bot.user}"
    )

# =====================================================
# START
# =====================================================
bot.run(TOKEN)
