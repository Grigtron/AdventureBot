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
logging.basicConfig(level=logging.DEBUG)

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
    

class ConfirmDeleteView(discord.ui.View):
        def __init__(self, user_id, bot, connection, cursor):
            super().__init__()
            self.user_id = user_id
            self.bot = bot
            self.connection = connection
            self.cursor = cursor
        
        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
        async def yes_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.response.defer()
            self.cursor.execute("DELETE FROM Character WHERE user_id = ?", (self.user_id,))
            self.connection.commit()
            await interaction.response.send_message("Your character has been deleted.")
            self.disable_buttons()

        @discord.ui.button(label="No", style=discord.ButtonStyle.red)
        async def no_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.response.send_message("Character deletion cancelled.")
            self.disable_buttons()

        def disable_buttons(self):
            for item in self.children:
                item.disabled = True
            
            self.stop()

asyncio.run(main())
