import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

CATEGORY_NAME = "Тест"  # Название категории, куда создавать каналы

# Модальное окно
class ChannelInfoModal(discord.ui.Modal, title="Создание канала"):
    nickname = discord.ui.TextInput(label="Ник", placeholder="Nick_Name", required=True)
    date = discord.ui.TextInput(label="Дата", placeholder="06.06.2025", required=True)
    level = discord.ui.TextInput(label="LVL", placeholder="2", required=True)
    type = discord.ui.TextInput(
        label="Тип", 
        placeholder="Собеседование / Восстановление / Лидерский пост (Гос/Нелегалы)",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        nick = self.nickname.value.strip()
        date = self.date.value.strip()
        level = self.level.value.strip()
        chan_type = self.type.value.strip()

        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

        if not category:
            category = await guild.create_category(CATEGORY_NAME)

        channel = await guild.create_text_channel(nick, category=category)
        msg = f"**{nick} | {date} | {level} | {chan_type}**"
        await channel.send(msg)
        await interaction.response.send_message(f"✅ Канал {channel.mention} создан!", ephemeral=True)

# Кнопка для запуска модалки
class CreateChannelView(discord.ui.View):
    @discord.ui.button(label="Создать канал", style=discord.ButtonStyle.success)
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChannelInfoModal())

@tree.command(name="create", description="Открыть меню создания канала")
async def create(interaction: discord.Interaction):
    await interaction.response.send_message("Нажмите кнопку ниже, чтобы создать канал:", view=CreateChannelView(), ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Synced {len(await tree.sync())} команд.")
    print(f"🔗 Бот запущен как {bot.user}")

bot.run(TOKEN)
