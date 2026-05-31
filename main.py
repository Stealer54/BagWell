import os
import json
import discord

from datetime import datetime
from discord.ext import commands
from discord.ui import View, Select
from dotenv import load_dotenv

# =====================================================
# Загрузка .env
# =====================================================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# =====================================================
# Discord
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
POINTS_FILE = "points.json"

FAMILIES_FILE = "families.json"

ISLAND_FILE = "island.json"

# =====================================================
# Дефолтные точки
# =====================================================
DEFAULT_POINTS = {
    "Баржа": "Свободно",
    "Старые Фибы (Noose)": "Свободно",
    "Притон": "Свободно",
    "ЛНС (каменоломня)": "Свободно",
    "Лес (лесопилка)": "Свободно",
    "Лабиринт (Kortz)": "Свободно"
}

# =====================================================
# Дефолтные семьи
# =====================================================
DEFAULT_FAMILIES = [
    "Obsidian",
    "Худричи",
    "Reseller",
    "Demorgan",
    "Giudice",
    "Velmora",
    "Fruktik"
]

# =====================================================
# Создание файлов
# =====================================================
if not os.path.exists(POINTS_FILE):

    with open(
        POINTS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            DEFAULT_POINTS,
            f,
            ensure_ascii=False,
            indent=4
        )

if not os.path.exists(FAMILIES_FILE):

    with open(
        FAMILIES_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            DEFAULT_FAMILIES,
            f,
            ensure_ascii=False,
            indent=4
        )

if not os.path.exists(ISLAND_FILE):

    island_data = {
        "Четверг": {
            "date": "12.06.2025",
            "places": {
                "1 место": "Obsidian",
                "2 место": "Худричи",
                "3 место": "Reseller"
            }
        },

        "Воскресение": {
            "date": "08.06.2025",
            "places": {
                "1 место": "Худричи",
                "2 место": "Reseller",
                "3 место": "Demorgan"
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
# JSON
# =====================================================
def load_points():

    with open(
        POINTS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

def save_points(data):

    with open(
        POINTS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

def load_families():

    with open(
        FAMILIES_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

def save_families(data):

    with open(
        FAMILIES_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

def load_island():

    with open(
        ISLAND_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

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
# EMBED POINTS
# =====================================================
def create_points_embed():

    data = load_points()

    embed = discord.Embed(
        title="📍 Удержание точек влияния",
        color=0x2b2d31
    )

    for point, family in data.items():

        embed.add_field(
            name=point,
            value=f"👑 {family}",
            inline=False
        )

    return embed

# =====================================================
# EMBED FAMILIES
# =====================================================
def create_families_embed():

    families = load_families()

    embed = discord.Embed(
        title="👑 Список семей",
        color=0x2b2d31
    )

    text = ""

    for i, family in enumerate(families, start=1):

        text += f"**{i}.** {family}\n"

    embed.description = text

    return embed

# =====================================================
# EMBED ISLAND
# =====================================================
def create_island_embed():

    data = load_island()

    embed = discord.Embed(
        title="🏝️ Удержание острова",
        color=0x2b2d31
    )

    thursday_date = datetime.strptime(
        data["Четверг"]["date"],
        "%d.%m.%Y"
    )

    sunday_date = datetime.strptime(
        data["Воскресение"]["date"],
        "%d.%m.%Y"
    )

    days = [
        ("Четверг", thursday_date),
        ("Воскресение", sunday_date)
    ]

    days.sort(
        key=lambda x: x[1]
    )

    for day_name, _ in days:

        info = data[day_name]

        text = ""

        for place, family in info["places"].items():

            text += (
                f"**{place}** — 👑 {family}\n"
            )

        embed.add_field(
            name=f"📍 {day_name}",
            value=(
                f"📅 **{info['date']}**\n\n"
                + text
            ),
            inline=False
        )

    return embed

# =====================================================
# SELECT FAMILY
# =====================================================
class FamilySelect(Select):

    def __init__(self):

        families = load_families()

        options = []

        for family in families:

            options.append(
                discord.SelectOption(
                    label=family
                )
            )

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

        family = self.values[0]

        await interaction.response.edit_message(
            content=(
                f"👑 Выбрана семья: "
                f"**{family}**\n\n"
                f"📍 Теперь выберите точку:"
            ),
            view=PointView(family),
            embed=None
        )

# =====================================================
# SELECT POINT
# =====================================================
class PointSelect(Select):

    def __init__(self, family_name):

        self.family_name = family_name

        data = load_points()

        options = []

        for point, owner in data.items():

            options.append(
                discord.SelectOption(
                    label=point,
                    description=f"Владелец: {owner}"
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

        point = self.values[0]

        data = load_points()

        data[point] = self.family_name

        save_points(data)

        embed = discord.Embed(
            title="✅ Точка обновлена",
            description=(
                f"📍 {point}\n"
                f"👑 {self.family_name}"
            ),
            color=0x00ff99
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None,
            content=None
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

    def __init__(self, family):

        super().__init__(timeout=None)

        self.add_item(
            PointSelect(family)
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

# =====================================================
# /families
# =====================================================
@tree.command(
    name="families",
    description="Список семей"
)
async def families(
    interaction: discord.Interaction
):

    embed = create_families_embed()

    await interaction.response.send_message(
        embed=embed
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
# /setallpoints
# =====================================================
@tree.command(
    name="setallpoints",
    description="Назначить семью на все точки"
)
async def setallpoints(
    interaction: discord.Interaction,
    family: str
):

    data = load_points()

    for point in data:

        data[point] = family

    save_points(data)

    await interaction.response.send_message(
        f"✅ Все точки теперь у семьи {family}",
        ephemeral=True
    )

# =====================================================
# /addfamily
# =====================================================
@tree.command(
    name="addfamily",
    description="Добавить семью"
)
async def addfamily(
    interaction: discord.Interaction,
    family: str
):

    families = load_families()

    if family in families:

        await interaction.response.send_message(
            "❌ Семья уже существует",
            ephemeral=True
        )

        return

    families.append(family)

    save_families(families)

    await interaction.response.send_message(
        f"✅ Семья {family} добавлена",
        ephemeral=True
    )

# =====================================================
# /removefamily
# =====================================================
@tree.command(
    name="removefamily",
    description="Удалить семью"
)
async def removefamily(
    interaction: discord.Interaction,
    family: str
):

    families = load_families()

    if family not in families:

        await interaction.response.send_message(
            "❌ Семья не найдена",
            ephemeral=True
        )

        return

    families.remove(family)

    save_families(families)

    await interaction.response.send_message(
        f"✅ Семья {family} удалена",
        ephemeral=True
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

    await interaction.response.send_message(
        "✅ Остров обновлен",
        ephemeral=True
    )

# =====================================================
# /setislanddate
# =====================================================
@tree.command(
    name="setislanddate",
    description="Настроить даты острова"
)
async def setislanddate(
    interaction: discord.Interaction,
    thursday_date: str,
    sunday_date: str
):

    data = load_island()

    data["Четверг"]["date"] = thursday_date

    data["Воскресение"]["date"] = sunday_date

    save_island(data)

    await interaction.response.send_message(
        "✅ Даты обновлены",
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
            "❌ Нет прав",
            ephemeral=True
        )

        return

    await interaction.response.defer(
        ephemeral=True
    )

    deleted = await interaction.channel.purge(
        limit=amount
    )

    await interaction.followup.send(
        f"🗑️ Удалено сообщений: {len(deleted)}",
        ephemeral=True
    )

# =====================================================
# READY
# =====================================================
@bot.event
async def on_ready():

    try:

        synced = await tree.sync()

        print(
            f"✅ Команд синхронизировано: {len(synced)}"
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
