import discord
from discord.ext import commands, tasks
import os
import asyncio
from itertools import cycle
from dotenv import load_dotenv

load_dotenv("token.env")
TOKEN: str = os.getenv("TOKEN")

bot = commands.Bot(command_prefix=".", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is online")

    try: 
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("An error with syncing application commands has occured: ", e)

@bot.tree.command(name="hello", description="Says hello back to the person who ran the command.")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} Hello There!") # ephemeral (only you can see this message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello there!, {ctx.author.mention}")

@bot.command(aliases=["gm", "morning"])
async def goodmorning(ctx):
    await ctx.send(f"Good morning, {ctx.author.mention}")

@bot.command()
async def sendembed(ctx):
    embeded_msg = discord.Embed(title="Title of embed", description="Description of embed", color=discord.Color.green())
    embeded_msg.set_author(name="Footer text", icon_url = ctx.author.avatar)
    embeded_msg.set_thumbnail(url=ctx.author.avatar)
    embeded_msg.add_field(name="Name of field", value="Value of field", inline=False)
    embeded_msg.set_image(url=ctx.guild.icon)
    embeded_msg.set_footer(text="Footer text", icon_url = ctx.author.avatar)
    await ctx.send(embed=embeded_msg)

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

asyncio.run(main())



