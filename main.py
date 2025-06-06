import discord
import random
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from database import *
from language import *

load_dotenv()  # load variables from .env
TOKEN = os.getenv("DISCORD_TOKEN")  # bot token to log in
GUILD = discord.Object(id=867657564883386438)  # test server
WHITELIST = {
    866878611063701525: "speaver",
    690179037397778477: "meoquan"
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class ChoCoBot(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}!")
        # sync slash commands to test server
        try:
            synced = await self.tree.sync(guild=GUILD)
            suffix = "" if len(synced) == 1 else "s"
            print(f"Synced {len(synced)} command{suffix} to Guild {GUILD.id}!")
        except Exception as e:
            print(f"Failed to sync: {e}")

    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        guild_id = message.guild.id
        content_std = strip_accents_lower(message.content)  # standardised content
        racism_words = get_racism_words(guild_id)

        if any(word in content_std for word in racism_words):
            count = increase_and_get_racism_count(user_id, guild_id)
            await message.channel.send(
                f"{message.author.mention}, bạn đã phân biệt chủng tộc {count} lần."
            )


bot = ChoCoBot(command_prefix="!", intents=intents)


@bot.tree.command(name="dm", description="du ma", guild=GUILD)
async def dm(interaction: discord.Interaction):
    # fromis_9(프로미스나인) \"DM\" M/V
    await interaction.response.send_message(
        r"https://youtu.be/4gXmClk8rKI"
    )


@bot.tree.command(name="pp", description="đo kích thước cậu nhỏ của bạn", guild=GUILD)
async def pp(interaction: discord.Interaction):
    low, high = (15.0, 30.0) if interaction.user.id in WHITELIST else (-5.0, 20.0)
    dick_len = round(random.uniform(low, high), 1)
    await interaction.response.send_message(
        f"{interaction.user.mention}, chim của bạn dài {dick_len} cm."
    )


@bot.tree.command(name="ynm", description="có? không? có thể?", guild=GUILD)
async def ynm(interaction: discord.Interaction):
    # Suzy(수지) \"Yes No Maybe\" M/V
    await interaction.response.send_message(
        r"https://youtu.be/b34ri3-uxks"
    )


@bot.tree.command(name="yoy", description="có hoặc có?", guild=GUILD)
async def yoy(interaction: discord.Interaction):
    # TWICE(트와이스) \"YES or YES\" M/V
    await interaction.response.send_message(
        r"https://youtu.be/mAKsZ26SabQ"
    )


@bot.tree.command(name="banword", description="thêm một từ vào danh sách pbct", guild=GUILD)
async def banword(interaction: discord.Interaction, word: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            f"{interaction.user.mention}, bạn không có quyền sử dụng lệnh này!"
        )
        return

    guild_id = interaction.guild.id
    user_id = interaction.user.id
    word = strip_accents_lower(word)

    if add_racism_word(word, guild_id, user_id):
        await interaction.response.send_message(
            f"{interaction.user.mention}, `{word}` đã được thêm vào danh sách pbct!"
        )
    else:
        await interaction.response.send_message(
            f"{interaction.user.mention}, `{word}` đã có trong danh sách pbct rồi!"
        )


@bot.tree.command(name="unbanword", description="xóa một từ khỏi danh sách pbct", guild=GUILD)
async def unbanword(interaction: discord.Interaction, word: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            f"{interaction.user.mention}, bạn không có quyền sử dụng lệnh này!"
        )
        return

    guild_id = interaction.guild.id
    word = strip_accents_lower(word)

    if remove_racism_word(word, guild_id):
        await interaction.response.send_message(
            f"{interaction.user.mention}, `{word}` đã được xóa khỏi danh sách pbct!"
        )
    else:
        await interaction.response.send_message(
            f"{interaction.user.mention}, `{word}` không tồn tại trong danh sách pbct!"
        )


create_users_per_guild_table()
create_racism_words_table()
bot.run(TOKEN)
