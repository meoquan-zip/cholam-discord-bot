import os
import discord
import random
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from language import strip_accents

load_dotenv()

TOKEN = os.getenv("TOKEN")  # bot token to log in
GUILD = discord.Object(id=867657564883386438)  # 12A4 server
WHITELIST = {
    866878611063701525: "speaver",
    690179037397778477: "meoquan"
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class Bot(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}!")

        try:
            synced = await self.tree.sync(guild=GUILD)
            suffix = "" if len(synced) == 1 else "s"
            print(f"Synced {len(synced)} command{suffix} to guild {GUILD.id}!")
        except Exception as e:
            print(f"Failed to sync: {e}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        content_std = strip_accents(message.content).lower()
        # print(f"{message.author}: {content_std}")

        if "dm cholam" in content_std:
            if message.guild is None:
                return
            member = message.guild.get_member(623127730678005780)  # cholam
            if member:
                await message.channel.send(f"dm {member.mention}")


bot = Bot(command_prefix="!", intents=intents)


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


bot.run(TOKEN)
