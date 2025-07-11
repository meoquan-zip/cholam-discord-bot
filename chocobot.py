import asyncio
import random

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from google import generativeai as genai

from database import *
from keep_alive import keep_alive
from language import normalise

load_dotenv()  # load environment variables from .env
keep_alive()  # prevent bot from automatically shutting down

GUILD = discord.Object(id=int(os.getenv('DISCORD_GUILD_ID')))  # test server
OWNERS = set(int(oid) for oid in os.getenv('DISCORD_OWNER_IDS').split(','))  # ids of bot owners

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class ChoCoBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            with open('genai/instruction.txt', encoding='utf-8') as f:
                system_instruction = f.read()
        except FileNotFoundError:
            print('Warning: instruction file not found, using default instruction')
            system_instruction = 'You are ChoCoBot, a helpful Discord bot assistant.'

        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.genai_model = genai.GenerativeModel(
            'gemini-2.0-flash',
            system_instruction=system_instruction
        )

    async def on_ready(self):
        print(f'Logged in as {self.user}!')

        try:  # initialise database
            init_database()
            print(f'Database initialised!')
        except Exception as e:
            print(f'Failed to initialise database: {e}')

        try:  # sync slash commands to test server
            synced = await self.tree.sync(guild=GUILD)
            suffix = '' if len(synced) == 1 else 's'
            print(f'{len(synced)} command{suffix} synced to Guild {GUILD.id}!')
        except Exception as e:
            print(f'Failed to sync commands: {e}')

    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = normalise(message.content)

        if not content:
            return

        user_id = message.author.id
        guild_id = message.guild.id
        racism_words = get_racism_words(guild_id)

        if any(word in content for word in racism_words):
            count = increase_and_get_racism_count(user_id, guild_id)
            await message.channel.send(
                f'{message.author.mention} bạn đã phân biệt chủng tộc {count} lần.'
            )


bot = ChoCoBot(command_prefix='!', intents=intents)


@bot.tree.command(name='10min', description='anh iem đợi tôi 10 phút', guild=GUILD)
async def slash_10_minutes(interaction: discord.Interaction):
    # Lee Hyori(이효리) "10 Minutes" M/V
    await interaction.response.send_message(
        'https://youtu.be/iKdr44yEBQU'
    )


@bot.tree.command(name='ask', description='trò chuyện với chatbot', guild=GUILD)
async def slash_ask(interaction: discord.Interaction,
                    prompt: app_commands.Range[str, 1, 150]):
    try:
        response = await asyncio.to_thread(bot.genai_model.generate_content, prompt)
        await interaction.response.send_message(
            f'{interaction.user.mention}: {prompt}\n\n{response.text}'
        )
    except Exception as e:
        print(f'Failed to generate response: {e}')
        await interaction.response.send_message(
            f'{interaction.user.mention} đã xảy ra lỗi kỹ thuật, xin hãy thử lại sau!'
        )


@bot.tree.command(name='bca', description='báo cáo anh chưa có ghế cho sếp ạ', guild=GUILD)
async def slash_bao_cao_anh(interaction: discord.Interaction):
    await interaction.response.send_message(
        'https://youtu.be/dgVrffcBMqA'
    )


@bot.tree.command(name='cl', description='chửi cholam', guild=GUILD)
async def slash_cholam(interaction: discord.Interaction):
    try:
        cholam = await bot.fetch_user(623127730678005780)
        await interaction.response.send_message(
            f'dm {cholam.mention}'
        )
    except discord.NotFound:
        await interaction.response.send_message(
            'ôi không, có vẻ như cholam đã chết rồi :( widepeepoSadge'
        )
    except discord.HTTPException:
        pass


@bot.tree.command(name='coin', description='tung đồng xu', guild=GUILD)
async def slash_coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(
        f'{interaction.user.mention} {"ngửa" if round(random.random()) else "sấp"}'
    )


@bot.tree.command(name='dm', description='du ma', guild=GUILD)
async def slash_dm(interaction: discord.Interaction):
    # fromis_9(프로미스나인) "DM" M/V
    await interaction.response.send_message(
        'https://youtu.be/4gXmClk8rKI'
    )


@bot.tree.command(name='pp', description='đo kích thước cậu nhỏ của bạn', guild=GUILD)
async def slash_pp(interaction: discord.Interaction):
    low, high = (15.0, 30.0) if interaction.user.id in OWNERS else (-5.0, 20.0)
    dick_len = round(random.uniform(low, high), 1)
    emote_len = round(-(-dick_len // 4) - 1)
    dick_emote = '' if emote_len < 0 else f':\t8{"-" if emote_len == 0 else "=" * emote_len + "D"}'
    await interaction.response.send_message(
        f'{interaction.user.mention} chim của bạn dài {dick_len} cm{dick_emote}'
    )


@bot.tree.command(name='ynm', description='có? không? có thể?', guild=GUILD)
async def slash_yes_no_maybe(interaction: discord.Interaction):
    # Suzy(수지) "Yes No Maybe" M/V
    await interaction.response.send_message(
        'https://youtu.be/b34ri3-uxks'
    )


@bot.tree.command(name='yoy', description='có hoặc có?', guild=GUILD)
async def slash_yes_or_yes(interaction: discord.Interaction):
    # TWICE(트와이스) "YES or YES" M/V
    await interaction.response.send_message(
        'https://youtu.be/mAKsZ26SabQ'
    )


@bot.tree.command(name='banword', description='thêm một từ vào danh sách cấm', guild=GUILD)
async def slash_ban_word(interaction: discord.Interaction,
                         word: app_commands.Range[str, 1, 20]):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            f'{interaction.user.mention} bạn không có quyền sử dụng lệnh này!'
        )
        return

    word_norm = normalise(word)

    if not word_norm:
        await interaction.response.send_message(
            f'{interaction.user.mention} từ bạn vừa nhập không hợp lệ!'
        )
        return

    guild_id = interaction.guild.id
    user_id = interaction.user.id

    if add_racism_word(word_norm, guild_id, user_id):
        await interaction.response.send_message(
            f'{interaction.user.mention} `{word}` đã được thêm vào danh sách cấm!'
        )
    else:
        await interaction.response.send_message(
            f'{interaction.user.mention} `{word}` đã có trong danh sách cấm rồi!'
        )


@bot.tree.command(name='unbanword', description='xóa một từ khỏi danh sách cấm', guild=GUILD)
async def slash_unban_word(interaction: discord.Interaction,
                           word: app_commands.Range[str, 1, 20]):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            f'{interaction.user.mention} bạn không có quyền sử dụng lệnh này!'
        )
        return

    word_norm = normalise(word)

    if not word_norm:
        await interaction.response.send_message(
            f'{interaction.user.mention} từ bạn vừa nhập không hợp lệ!'
        )
        return

    guild_id = interaction.guild.id

    if remove_racism_word(word_norm, guild_id):
        await interaction.response.send_message(
            f'{interaction.user.mention} `{word}` đã được xóa khỏi danh sách cấm!'
        )
    else:
        await interaction.response.send_message(
            f'{interaction.user.mention} `{word}` không tồn tại trong danh sách cấm!'
        )


bot.run(os.getenv('DISCORD_TOKEN'))
