import os
import json
import discord
from discord.ext import commands
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
# Семьи
# =====================================================
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

# =====================================================
# Места острова
# =====================================================
ISLAND_PLACES = [
    "1 место",
    "2 место",
    "3 место"
]

# =====================================================
# Создание points.json
# =====================================================
if not os.path.exists(DATA_FILE):

    with open(DATA_FILE, "w", encoding="utf-8") as f:

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
        "Четверг": {
            "1 место": "Свободно",
            "2 место": "Свободно",
            "3 место": "Свободно"
        },
        "Воскресение": {
            "1 место": "Свободно",
            "2 место": "Свободно",
            "3 место": "Свободно"
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

    with open(DATA_FILE, "r", encoding="utf-8") as f:

        return json.load(f)

# =====================================================
# Сохранение points
# =====================================================
def save_points(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:

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
# Embed families
# =====================================================
def create_families_embed():

    embed = discord.Embed(
        title="👑 Список семей",
        color=0x2b2d31
    )

    for family in FAMILIES:

        embed.add_field(
            name="Семья",
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
        title="🏝️ Распределение острова",
        color=0x2b2d31
    )

    for day, places in data.items():

        text = ""

        for place, family in places.items():

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
# Сохранение сообщения points
# =====================================================
def save_points_message(
    channel_id,
    message_id
):

    data = {
        "channel_id": channel_id,
        "message_id": message_id
    }

    with open(
        POINTS_MESSAGE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(data, f)

# =====================================================
# Загрузка сообщения points
# =====================================================
def load_points_message():

    if not os.path.exists(
        POINTS_MESSAGE_FILE
    ):

        return None

    with open(
        POINTS_MESSAGE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# =====================================================
# Сохранение сообщения families
# =====================================================
def save_families_message(
    channel_id,
    message_id
):

    data = {
        "channel_id": channel_id,
        "message_id": message_id
    }

    with open(
        FAMILIES_MESSAGE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(data, f)

# =====================================================
# Загрузка сообщения families
# =====================================================
def load_families_message():

    if not os.path.exists(
        FAMILIES_MESSAGE_FILE
    ):

        return None

    with open(
        FAMILIES_MESSAGE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# =====================================================
# Сохранение island message
# =====================================================
def save_island_message(
    channel_id,
    message_id
):

    data = {
        "channel_id": channel_id,
        "message_id": message_id
    }

    with open(
        ISLAND_MESSAGE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(data, f)

# =====================================================
# Загрузка island message
# =====================================================
def load_island_message():

    if not os.path.exists(
        ISLAND_MESSAGE_FILE
    ):

        return None

    with open(
        ISLAND_MESSAGE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# =====================================================
# Автообновление points
# =====================================================
async def update_points_message():

    data = load_points_message()

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
            embed=create_points_embed()
        )

    except:

        pass

# =====================================================
# Автообновление families
# =====================================================
async def update_families_message():

    data = load_families_message()

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
            embed=create_families_embed()
        )

    except:

        pass

# =====================================================
# Автообновление island
# =====================================================
async def update_island_message():

    data = load_island_message()

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
            embed=create_island_embed()
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

        await update_points_message()

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
# VIEW FAMILY
# =====================================================
class FamilyView(View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            FamilySelect()
        )

# =====================================================
# VIEW POINT
# =====================================================
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

    save_points_message(
        interaction.channel.id,
        message.id
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

    message = await interaction.original_response()

    save_families_message(
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

    save_island_message(
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

    if family in FAMILIES:

        await interaction.response.send_message(
            "❌ Семья уже существует.",
            ephemeral=True
        )

        return

    FAMILIES.append(family)

    await update_families_message()

    embed = discord.Embed(
        title="✅ Семья добавлена",
        description=f"👑 {family}",
        color=0x00ff99
    )

    await interaction.response.send_message(
        embed=embed,
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

    if family not in FAMILIES:

        await interaction.response.send_message(
            "❌ Семья не найдена.",
            ephemeral=True
        )

        return

    FAMILIES.remove(family)

    await update_families_message()

    embed = discord.Embed(
        title="🗑️ Семья удалена",
        description=f"👑 {family}",
        color=0xff0000
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

# =====================================================
# /setisland
# =====================================================
@tree.command(
    name="setisland",
    description="Назначить семью на остров"
)
@app_commands.describe(
    day="День",
    place="Место",
    family="Семья"
)
@app_commands.choices(
    day=[
        app_commands.Choice(
            name="Четверг",
            value="Четверг"
        ),
        app_commands.Choice(
            name="Воскресение",
            value="Воскресение"
        )
    ],
    place=[
        app_commands.Choice(
            name="1 место",
            value="1 место"
        ),
        app_commands.Choice(
            name="2 место",
            value="2 место"
        ),
        app_commands.Choice(
            name="3 место",
            value="3 место"
        )
    ]
)
async def setisland(
    interaction: discord.Interaction,
    day: app_commands.Choice[str],
    place: app_commands.Choice[str],
    family: str
):

    data = load_island()

    data[day.value][place.value] = family

    save_island(data)

    await update_island_message()

    embed = discord.Embed(
        title="✅ Остров обновлен",
        color=0x00ff99
    )

    embed.add_field(
        name="📅 День",
        value=day.value,
        inline=False
    )

    embed.add_field(
        name="🏆 Место",
        value=place.value,
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
# READY
# =====================================================
@bot.event
async def on_ready():

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
