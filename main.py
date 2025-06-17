import os
import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Select, Modal, TextInput
from dotenv import load_dotenv

# Загрузка .env файла
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # ← Теперь переменная определена!
CATEGORY_NAME = "Характеристики"     # Название категории

# Настройка бота
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# --- Модалка для сбора данных ---
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
        message = f"{self.nickname.value} | {self.date.value} | {self.level.value} | {self.channel_type_value}"
        await channel.send(message)

        await interaction.response.send_message(f"✅ Канал {channel.mention} создан!", ephemeral=True)

# --- Выбор типа заявки ---
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

# --- View с селектом ---
class CreateChannelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ChannelTypeSelect())

# --- Команда /create ---
@tree.command(name="create", description="Создать канал по заявке")
async def create(interaction: Interaction):
    view = CreateChannelView()
    await interaction.response.send_message("🔽 Выберите тип заявки:", view=view, ephemeral=True)

# --- Запуск и синхронизация ---
@bot.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Ошибка sync: {e}")
    print(f"🔗 Logged in as {bot.user}")

bot.run(TOKEN)
