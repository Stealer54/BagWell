import discord
from discord.ui import View, Select

POINTS = [
    "Баржа",
    "Старые Фибы (Noose)",
    "Притон",
    "ЛНС (каменоломня)",
    "Лес (лесопилка)",
    "Лабиринт (Kortz)"
]

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
# SELECT СЕМЬИ
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

        # сохраняем выбранную семью
        self.view.selected_family = self.values[0]

        await interaction.response.edit_message(
            content=(
                f"👑 Семья: "
                f"**{self.view.selected_family}**\n\n"
                f"📍 Теперь выберите точку:"
            ),
            view=PointView(
                self.view.selected_family
            )
        )

# =========================
# SELECT ТОЧЕК
# =========================
class PointSelect(Select):

    def __init__(
        self,
        family_name
    ):

        self.family_name = family_name

        options = [
            discord.SelectOption(
                label=point,
                description="Нажмите для выбора"
            )
            for point in POINTS
        ]

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

        self.selected_family = None

        self.add_item(
            FamilySelect()
        )

# =========================
# VIEW ТОЧЕК
# =========================
class PointView(View):

    def __init__(
        self,
        family_name
    ):

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
