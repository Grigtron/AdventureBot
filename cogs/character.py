import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import math
import random
import asyncio
import time

class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.physique = "normal"
        self.intelligence = "normal"
        self.luck = "normal"
        self.name = ""
        self.creating_character = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Character is online")
  
    @app_commands.command(name="create", description="Create a new character")
    async def create(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        user_id = interaction.user.id

        if user_id in self.creating_character:
            time_left = 30 - (time.time() - self.creating_character[user_id])
            if time_left > 0:
                await interaction.followup.send(f"You're already creating a character. Please wait {int(time_left)} second(s).")
                return
            if time_left == 0:
                del self.creating_character[user_id]
        
        self.creating_character[user_id] = time.time()        

        connection = sqlite3.connect("character.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Character WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        if result:
            await interaction.followup.send("You already have a character! Please /delete your character or /start your adventure!", ephemeral=True)
            if user_id in self.creating_character:
                del self.creating_character[user_id]
        else:
            await interaction.delete_original_response()
            await self.create_character(interaction)
                
        connection.close()
    
    async def create_character(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        try:
            dm_channel = await interaction.user.create_dm()
            await dm_channel.send("Please choose a name for your character.")

            connection = sqlite3.connect("character.db")
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM Character WHERE user_id = ?", (interaction.user.id,))
            result = cursor.fetchone()
            
            if result:
                await dm_channel.send("You already have a character! Please use /delete to delete your current character or ignore this message.")
                connection.close()
                return

            def check(msg):
                return msg.author == interaction.user and isinstance(msg.channel, discord.DMChannel)
            
            message = await self.bot.wait_for("message", check=check, timeout=60)
            character_name = message.content.strip()

            await dm_channel.send("Choose your physique: Strong, Normal, or Weak.")
            message = await self.bot.wait_for("message", check=check, timeout=60)
            physique = message.content.strip().lower()
            if physique not in ["strong", "normal", "weak"]:
                await dm_channel.send("Invalid choice. Defaulting to 'normal'.")
                physique = "normal"

            await dm_channel.send("Choose your intelligence: Genius, Normal, or Dim.")
            message = await self.bot.wait_for("message", check=check, timeout=60)
            intelligence = message.content.strip().lower()
            if intelligence not in ["genius", "normal", "dim"]:
                await dm_channel.send("Invalid choice. Defaulting to 'normal'.")
                intelligence = "normal"

            await dm_channel.send("Choose your luck: Lucky, Normal, or Unlucky.")
            message = await self.bot.wait_for("message", check=check, timeout=60)
            luck = message.content.strip().lower()
            if luck not in ["lucky", "normal", "unlucky"]:
                await dm_channel.send("Invalid choice. Defaulting to 'normal'.")
                luck = "normal"
            
            
            cursor.execute("INSERT INTO Character (user_id, name, physique, intelligence, luck) VALUES (?, ?, ?, ?, ?)",
                            (interaction.user.id, character_name, physique, intelligence, luck))
            connection.commit()
            connection.close()

        
            await dm_channel.send(f"Character created!\n**Name**: {character_name.capitalize()}\n**Physique**: {physique.capitalize()}\n**Intelligence:** {intelligence.capitalize()}\n**Luck:** {luck.capitalize()}\nIf you would like to change anything please /delete your character and /create it again. To start the game please use /start")
            

        except discord.Forbidden:
            await interaction.followup.send("Please enable DMs for this server")
        except asyncio.TimeoutError:
            await dm_channel.send("You took too long to respond. Please try again.")
        except Exception as e:
            await dm_channel.send(f"An unexpected error occurred: {e}")
        finally:
            del self.creating_character[user_id]

    @app_commands.command(name="delete", description="Delete your character")
    async def delete_character(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        connection = sqlite3.connect("character.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Character WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()


        if not result:
            await interaction.response.send_message("You don't have a character to delete")
            connection.close()
            return
        
        await interaction.response.send_message("Are you sure you want to delete your character? (Yes or No)")

        def check(msg):
            return msg.author.id == user_id and msg.channel == interaction.channel and msg.content.lower() in ["yes", "no"]
        try: 
            msg = await self.bot.wait_for("message", check=check, timeout=30)

            if msg.content.lower() == "yes":
                cursor.execute("DELETE FROM Character WHERE user_ID = ?", (user_id,))
                cursor.execute("DELETE FROM PlayerProgress WHERE user_id = ?", (user_id,))
                connection.commit()
                await interaction.followup.send("Your character has been deleted.")
            else:
                await interaction.followup.send("Character deletion cancelled.")
        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. Please run the command again")
        
        connection.close()


async def setup(bot):
    print("Loading Character Cog...")
    await bot.add_cog(Character(bot))