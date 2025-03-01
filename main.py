from dotenv import load_dotenv
import discord
import os
import asyncio
from itertools import cycle
from discord.ext import commands, tasks
from discord import app_commands
import logging

load_dotenv(".env")
TOKEN: str = os.getenv("TOKEN")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot_statuses = "a great adventure!"
##logging.basicConfig(level=logging.DEBUG)

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            
async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

@bot.event
async def on_ready():
    print("Bot ready!")
    #change_bot_status.start()
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("An error with syncing application commands has occurred: ", e)
    

asyncio.run(main())
