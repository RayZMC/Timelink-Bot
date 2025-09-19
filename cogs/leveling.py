import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import math
import random

class LevelSys(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Leveling is online!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        connection = sqlite3.connect("./cogs/levels.db")
        cursor = connection.cursor()
        guild_id = message.guild.id
        user_id = message.author.id 

        # Primary Key
        cursor.execute("SELECT * FROM Users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        
        result = cursor.fetchone()

        # If user is not in the database
        if result is None:
            cur_level = 0
            xp = 0
            level_up_xp = 100
            cursor.execute("INSERT INTO Users (guild_id, user_id, level, xp, level_up_xp) Values (?,?,?,?,?)", (guild_id, user_id, cur_level, xp, level_up_xp))
        # If user is in the database
        else:
            cur_level = result[2]
            xp = result[3]
            level_up_xp = result[4]

            # Add xp
            xp += random.randint(1,25)
        
        if xp >= level_up_xp:
            cur_level += 1
            new_level_up_xp = math.ceil(50 * cur_level ** 2 + 100 * cur_level + 50)

            await message.channel.send(f"{message.author.mention} has leveled up to level {cur_level}!")
            cursor.execute("UPDATE Users SET level = ?, xp = ?, level_up_xp = ? WHERE guild_id = ? AND user_id = ?", (cur_level, xp, new_level_up_xp, guild_id, user_id))
        
        cursor.execute("UPDATE Users SET xp = ? WHERE guild_id = ? AND user_id = ?", (xp, guild_id, user_id))

        connection.commit()
        connection.close()

    # Checking a members level
    @app_commands.command(name="level", description="Sends the level card for a given user.")
    async def level(self, interaction: discord.Interaction, member: discord.Member=None):
        if member is None:
            member = interaction.user
        
        member_id = member.id
        guild_id = interaction.guild.id
        
        connection = sqlite3.connect("./cogs/levels.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE guild_id = ? AND user_id = ?", (guild_id, member_id))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message(f"{member.name} currently does not have a level.")
        else:
            level = result[2]
            xp =  result[3]
            level_up_xp = result[4]

            await interaction.response.send_message(f"Level statistics for {member.name}: \nLevel: {level} \nXP: {xp} \nXP To Level Up: {level_up_xp}")
        
        connection.close()




async def setup(bot):
    await bot.add_cog(LevelSys(bot))