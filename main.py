import os
import json
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select
from dotenv import load_dotenv

# =========================
# Загрузка .env
# =========================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

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

        json.dump(
            default_points,
            f,
            ensure_ascii=False,
            indent=4
        )

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

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

# =========================
# EMBED ТОЧЕК
# =========================
def create_points_embed():

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

    return embed

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
# SELECT УДАЛЕНИЯ СЕМЬИ
# =========================
class RemoveFamilySelect(Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label=family
            )

            for family in FAMILIES
        ]

        super().__init__(
            placeholder="Выберите семью для удаления",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        selected_family = self.values[0]

        if selected_family not in FAMILIES:

            await interaction.response.send_message(
                "❌ Семья не найдена.",
                ephemeral=True
            )

            return

        FAMILIES.remove(selected_family)

        embed = discord.Embed(
            title="✅ Семья удалена",
            description=f"👑 {selected_family}",
            color=0xff0000
        )

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

# =========================
# VIEW УДАЛЕНИЯ
# =========================
class RemoveFamilyView(View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            RemoveFamilySelect()
        )

# =========================
# SELECT ДЛЯ /setallpoints
# =========================
class SetAllPointsSelect(Select):

    def __init__(self, point_name):

        self.point_name = point_name

        options = [

            discord.SelectOption(
                label=family
            )

            for family in FAMILIES
        ]

        super().__init__(
            placeholder=f"{point_name}",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        points_data = load_points()

        selected_family = self.values[0]

        points_data[self.point_name] = selected_family

        save_points(points_data)

        await interaction.response.defer()

        try:

            await interaction.message.edit(
                embed=create_points_embed(),
                view=SetAllPointsView()
            )

        except:
            pass

# =========================
# VIEW /setallpoints
# =========================
class SetAllPointsView(View):

    def __init__(self):

        super().__init__(timeout=None)

        for point in default_points.keys():

            self.add_item(
                SetAllPointsSelect(point)
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

    embed = discord.Embed(
        title="👑 Выберите семью",
        color=0x2b2d31
    )

    await interaction.response.send_message(
        embed=embed,
        view=FamilyView(),
        ephemeral=True
    )

# =========================
# /setallpoints
# =========================
@tree.command(
    name="setallpoints",
    description="Быстро назначить все точки"
)
async def setallpoints(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        embed=create_points_embed(),
        view=SetAllPointsView(),
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

    embed = create_points_embed()

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

    embed = discord.Embed(
        title="✅ Семья добавлена",
        description=f"👑 {family}",
        color=0x00ff99
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

# =========================
# /removefamily
# =========================
@tree.command(
    name="removefamily",
    description="Удалить семью"
)
async def removefamily(
    interaction: discord.Interaction
):

    if len(FAMILIES) == 0:

        await interaction.response.send_message(
            "❌ Список семей пуст.",
            ephemeral=True
        )

        return

    embed = discord.Embed(
        title="🗑️ Выберите семью",
        color=0x2b2d31
    )

    await interaction.response.send_message(
        embed=embed,
        view=RemoveFamilyView(),
        ephemeral=True
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
        embed=embed,
        ephemeral=True
    )

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

        print(
            f"❌ Ошибка sync: {e}"
        )

    print(
        f"✅ Бот запущен как {bot.user}"
    )

# =========================
# START
# =========================
bot.run(TOKEN)
