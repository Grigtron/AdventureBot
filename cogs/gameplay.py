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
                story_connection = sqlite3.connect("storynodes.db")
                story_cursor = story_connection.cursor()

                story_key = progress[1]
                print(f"User's story_key: {story_key}")
                story_cursor.execute("SELECT * FROM StoryNodes WHERE key = ?", (str(story_key),))
                story_node = story_cursor.fetchone()

                if story_node:
                    print(f"Loaded story node: {story_node}")
                    story_text = story_node[1]
                    choices_json = story_node[2]
                    choices = json.loads(choices_json)

                    response_message = (f"{story_text}\n\nChoices:\n")
                    for choice_key, choice_text in choices.items():
                        response_message += f"{choice_key}: {choice_text}\n"
                    await interaction.followup.send(response_message)
                else:
                    print (f"No story node found for story_key: {story_key}")
                    await interaction.followup.send("There was an issue loading your story progress.")

        finally:
            connection.close()



async def setup(bot):
    print ("Loading Gameplay Cog...")
    await bot.add_cog(Gameplay(bot))