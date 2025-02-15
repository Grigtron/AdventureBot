import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import sqlite3
import json

class Gameplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Gameplay is online")

    @app_commands.command(name="start", description="Begin your adventure!")
    async def start(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        user_id = interaction.user.id
        connection = sqlite3.connect("character.db")
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM Character WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if not result:
                dm_channel = await interaction.user.create_dm()
                await dm_channel.send("Please create a character first using the /create command")
                return
            
            cursor.execute("SELECT * FROM PlayerProgress WHERE user_id = ?", (user_id,))
            progress = cursor.fetchone()

            if not progress:
                cursor.execute("INSERT INTO PlayerProgress (user_id, story_key) VALUES (?, ?)", (user_id, '1'))
                connection.commit()
                await interaction.followup.send("Your adventure begins now!")

            else:
                story_key = progress[1]
                cursor.execute("SELECT * FROM StoryNodes WHERE key = ?", (story_key,))
                story_node = cursor.fetchone()

                if story_node:
                    await interaction.followup.send("Loading story progress...")
                else:
                    await interaction.followup.send("There was an issue loading your story progress.")

        finally:
            connection.close()
            await interaction.delete_original_response()



async def setup(bot):
    print ("Loading Gameplay Cog...")
    await bot.add_cog(Gameplay(bot))