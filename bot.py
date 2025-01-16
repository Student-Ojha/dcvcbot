import discord
from discord.ext import commands
import os

# Bot setup
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Logging for startup
@bot.event
async def on_ready():
    print(f"Bot has successfully started!")
    print(f"Logged in as: {bot.user}")
    print(f"Connected to guilds: {[guild.name for guild in bot.guilds]}")

# Voice state update event
@bot.event
async def on_voice_state_update(member, before, after):
    print(f"Voice state updated for {member.name}: Before: {before.channel}, After: {after.channel}")
    if before.channel is None and after.channel is not None:
        print(f"{member.name} joined {after.channel.name}")

# Start the bot
print("Starting Discord bot...")
bot.run(os.environ['DISCORD_BOT_TOKEN'])
