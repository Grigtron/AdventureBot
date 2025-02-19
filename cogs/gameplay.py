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
    
    def get_player_progress(self, user_id):
        connection = sqlite3.connect("character.db")
        cursor = connection.cursor()
        cursor.execute("SELECT story_key FROM PlayerProgress WHERE user_id = ?", (user_id,))
        progress = cursor.fetchone()

        connection.close()
        return progress[0] if progress else "Error loading player progress."
    
    def get_story_node(self, story_key):
        connection = sqlite3.connect("storynodes.db")
        cursor = connection.cursor()
        cursor.execute("SELECT story_text, choices FROM StoryNodes WHERE key = ?", (str(story_key),))
        story_node = cursor.fetchone()

        connection.close()
        return story_node if story_node else None

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
                await interaction.followup.send("Your adventure begins now! Please run /start again.")
                print(f"Inserted player with story_key 1 for user {user_id}")

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

    @app_commands.command(name="choose", description="Make your choice!")
    async def choice(self, interaction: discord.Interaction, choice_number: int):
        await interaction.response.defer(thinking=True)
            
        user_id = interaction.user.id
        story_key = self.get_player_progress(user_id)

        if not story_key:
            await interaction.followup.send("You haven't /start-ed an adventure yet!")
            return
        
        story_node = self.get_story_node(story_key)
        if not story_node:
            await interaction.followup.send("There was an issue loading your current story progress.")
            return
        
        story_text, choices_json = story_node
        choices = json.loads(choices_json)
        print(f"Choices loaded: {choices}")  # Debug to inspect choices

        choice_key = str(choice_number)
        if choice_key not in choices:
            await interaction.followup.send(f"Invalid choice. Please /choose a valid choice.")

        next_story_key = choice_key
        print(f"Next story key for choice {choice_key}: {next_story_key}")

        connection = sqlite3.connect("character.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE PlayerProgress SET story_key = ? WHERE user_id = ?", (next_story_key, user_id))
        connection.commit()
        print(f"Updated story_key to {next_story_key} for user {user_id}")
        connection.close()

        print(f"Fetching new story node for key: {next_story_key}")
        new_story_node = self.get_story_node(next_story_key)
        print(f"New story node: {new_story_node}")
        
        if not new_story_node:
            await interaction.followup.send("The story ends here... for now!")
            return
        
        new_story_text, new_choices_json = new_story_node
        new_choices = json.loads(new_choices_json)

        formatted_choices = "\n".join([f"{key}: {text}" for key, text in new_choices.items()])
        await interaction.followup.send(f"{new_story_text}\n\n**Choices:**\n{formatted_choices}")




async def setup(bot):
    print ("Loading Gameplay Cog...")
    await bot.add_cog(Gameplay(bot))