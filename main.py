import discord
from discord.ext import commands
import subprocess
import psutil
import os
import random
import time
from datetime import datetime
from discord import Embed
import matplotlib.pyplot as plt

bot = commands.Bot(command_prefix='.')

running = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

bot.remove_command("help")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")
    
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "fia" in message.content.lower():
        await message.reply("# rome: <:emoji_17:1465090398148890976>")

    await bot.process_commands(message)
 

@bot.command()
@commands.is_owner()
async def reload(ctx, cog: str):
    embed = Embed(color=discord.Color.from_rgb(248, 200, 220))
    try:
        bot.unload_extension(f"cogs.{cog}")
        bot.load_extension(f"cogs.{cog}")
        embed.title = "<:emoji_3:1465089507610067045> Cog Reloaded"
        embed.description = f"> Successfully reloaded **{cog}**"
    except Exception as e:
        embed.title = "<:emoji_5:1465089560227741917> Reload Failed"
        embed.description = f">>> Could not reload **{cog}**\n```py\n{e}\n```"
    embed.set_footer(text="I <3 fia")
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def load(ctx, cog: str):
    embed = Embed(color=discord.Color.from_rgb(248, 200, 220))
    try:
        bot.load_extension(f"cogs.{cog}")
        embed.title = "<:emoji_10:1465089797511975159> Cog Loaded"
        embed.description = f"> Successfully loaded **{cog}**"
    except Exception as e:
        embed.title = "<:emoji_5:1465089560227741917> Load Failed"
        embed.description = f">>> Could not load **{cog}**\n```py\n{e}\n```"
    embed.set_footer(text="I <3 fia")
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def unload(ctx, cog: str):
    embed = Embed(color=discord.Color.from_rgb(248, 200, 220))
    try:
        bot.unload_extension(f"cogs.{cog}")
        embed.title = "<:emoji_10:1465089797511975159> Cog Unloaded"
        embed.description = f"> Successfully unloaded **{cog}**"
    except Exception as e:
        embed.title = "<:emoji_5:1465089560227741917> Unload Failed"
        embed.description = f">>> Could not unload **{cog}**\n```py\n{e}\n```"
    embed.set_footer(text="I <3 fia")
    await ctx.send(embed=embed)

    
@bot.command()
async def run(ctx, filename):
    embed = discord.Embed()
    embed.set_footer(text="I <3 fia")

    if filename in running:
        embed.description = "# <:emoji_11:1465089832010383423> **Already running**\n\n > This file is currently active."
        embed.color = discord.Color.from_rgb(248, 200, 220)
        await ctx.send(embed=embed)
        return

    if not os.path.isfile(filename):
        embed.description = "# <:emoji_13:1465090223133167880> **File not found**\n\n > The specified file does not exist."
        embed.color = discord.Color.from_rgb(248, 200, 220)
        await ctx.send(embed=embed)
        return

    proc = subprocess.Popen(['python', filename])
    running[filename] = proc

    embed.description = (
        "# <:emoji_10:1465089797511975159> **Started successfully**\n\n"
        f">>> **File:** `{filename}`\n"
        f"**PID:** `{proc.pid}`"
    )
    embed.color = discord.Color.from_rgb(248, 200, 220)
    await ctx.send(embed=embed)


@bot.command()
async def kill(ctx, filename):
    proc = running.get(filename)

    embed = discord.Embed(
        color=discord.Color.from_rgb(248, 200, 220)
    )
    embed.set_footer(text="I <3 fia")

    if not proc:
        embed.description = "# <:emoji_2:1465089477818056799> **Not running**\n\n> That file isnât currently active."
        await ctx.send(embed=embed)
        return

    proc.terminate()
    running.pop(filename)

    embed.description = f"# <:emoji_10:1465089797511975159>  **Killed**\n\n> Successfully stopped `{filename}`."
    await ctx.send(embed=embed)


@bot.command(name='list')
async def list_cmd(ctx):
    embed = discord.Embed(
        color=discord.Color.from_rgb(248, 200, 220)
    )
    embed.set_footer(text="I <3 fia")

    if not running:
        embed.description = "<:emoji_2:1465089477818056799> **No running processes**"
        await ctx.send(embed=embed)
        return

    description = ""
    for name, proc in running.items():
        description += f"â¢ `{name}` â PID `{proc.pid}`\n"

    embed.description = f"# <:emoji_3:1465089507610067045> **Running processes**\n\n> {description}"
    await ctx.send(embed=embed)
@bot.command()
async def stats(ctx, filename):
    proc = running.get(filename)

    embed = discord.Embed(
        color=discord.Color.from_rgb(248, 200, 220)
    )
    embed.set_footer(text="I <3 fia")

    if not proc:
        embed.description = "# <:emoji_18:1465090418311172197> **Not running**"
        await ctx.send(embed=embed)
        return

    try:
        p = psutil.Process(proc.pid)

        cpu = p.cpu_percent(interval=0.4)
        ram_mb = p.memory_info().rss / 1024 / 1024
        threads = p.num_threads()
        status = p.status()

        uptime_seconds = int(time.time() - p.create_time())
        uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_seconds))

        chart_path = f"stats_{proc.pid}.png"

        plt.figure()
        plt.bar(["CPU %", "RAM MB"], [cpu, ram_mb], color=["#FF69B4", "#FFB6C1"])
        plt.title("Process Resource Usage")
        plt.ylabel("Usage")
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        embed.title = f"# <:emoji_13:1465090223133167880> Stats for `{filename}`"
        embed.description = (
            f">>> **CPU:** `{cpu:.1f}%`\n"
            f"**RAM:** `{ram_mb:.1f} MB`\n"
            f"**Threads:** `{threads}`\n"
            f"**Status:** `{status}`\n"
            f"**Uptime:** `{uptime}`"
        )

        file = discord.File(chart_path, filename="stats.png")
        embed.set_image(url="attachment://stats.png")

        await ctx.send(embed=embed, file=file)

        os.remove(chart_path)

    except psutil.NoSuchProcess:
        running.pop(filename, None)
        embed.description = "# <:emoji_18:1465090418311172197> **Process ended**"
        await ctx.send(embed=embed)
    

bot.run('token_here')
