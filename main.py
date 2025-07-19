import os
import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Select, Modal, TextInput
from dotenv import load_dotenv

# Загрузка .env файла
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # Убедитесь, что токен задан в .env
CATEGORY_NAME = "Характеристики"  # Название категории, куда будут создаваться каналы

# Настройка бота
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# --- Модалка для сбора данных при создании канала ---
class ChannelInfoModal(Modal, title="Данные для создания канала"):
    nickname = TextInput(label="Ник", placeholder="Пример: Jacob_Stealer")
    date = TextInput(label="Дата", placeholder="Пример: 06.06.2025")
    level = TextInput(label="LVL", placeholder="Пример: 2")

    def __init__(self, channel_type: str):
        super().__init__()
        self.channel_type_value = channel_type

    async def on_submit(self, interaction: Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

        if category is None:
            await interaction.response.send_message("❌ Категория 'Характеристики' не найдена.", ephemeral=True)
            return

        channel_name = self.nickname.value.strip().replace(" ", "_")
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message("⚠️ Канал с таким ником уже существует.", ephemeral=True)
            return

        channel = await guild.create_text_channel(name=channel_name, category=category)

        nickname = self.nickname.value.strip()
        date = self.date.value.strip()
        level = self.level.value.strip()
        message = f"[{nickname}](https://arizonarp.logsparser.info/?server_number=5&sort=desc&player={nickname}) | {date} | {level} | {self.channel_type_value}"
        await channel.send(message)

        await interaction.response.send_message(f"✅ Канал {channel.mention} создан!", ephemeral=True)

# --- Селект выбора типа заявки ---
class ChannelTypeSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Собеседование"),
            discord.SelectOption(label="Восстановление"),
            discord.SelectOption(label="Лидерский пост (Гос)"),
            discord.SelectOption(label="Лидерский пост (Нелегалы)")
        ]
        super().__init__(placeholder="Выберите тип заявки", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(ChannelInfoModal(channel_type=self.values[0]))

class CreateChannelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ChannelTypeSelect())

@tree.command(name="create", description="Создать канал по заявке")
async def create(interaction: Interaction):
    view = CreateChannelView()
    await interaction.response.send_message("🔽 Выберите тип заявки:", view=view, ephemeral=True)

# --- Логика /log команды с embed сообщением ---
class LogTypeSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Заслуги", emoji="✅"),
            discord.SelectOption(label="Косяк", emoji="⚠️")
        ]
        super().__init__(placeholder="Выберите тип", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(LogDescriptionModal(log_type=self.values[0]))

class LogDescriptionModal(Modal, title="Описание действия"):
    def __init__(self, log_type: str):
        super().__init__()
        self.log_type = log_type
        self.desc_input = TextInput(label="Что сделал игрок", style=discord.TextStyle.paragraph)
        self.add_item(self.desc_input)

    async def on_submit(self, interaction: Interaction):
        description = self.desc_input.value.strip()
        color = discord.Color.green() if self.log_type == "Заслуги" else discord.Color.red()

        embed = discord.Embed(
            title=f"**{self.log_type.upper()}**",
            description=description,
            color=color
        )

        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Лог добавлен!", ephemeral=True)

class LogView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(LogTypeSelect())

@tree.command(name="log", description="Добавить лог: Заслуга или Косяк")
async def log(interaction: Interaction):
    await interaction.response.send_message("Выберите тип:", view=LogView(), ephemeral=True)

# --- Запуск бота ---
@bot.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Ошибка sync: {e}")
    print(f"🔗 Logged in as {bot.user}")

bot.run(TOKEN)
