import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# Flask app setup for keeping the bot alive
app = Flask('')


@app.route('/')
def home():
    return "VC Notification Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# Bot setup
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True  # Required to detect member activities
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration
NOTIFICATION_CHANNEL_NAME = "vc-notifications"  # Replace with your text channel name


# Startup Logging
print("Attempting to start the bot...")


@bot.event
async def on_ready():
    print("Bot has successfully started!")
    print(f"Logged in as: {bot.user}")
    print(f"Connected to guilds: {[guild.name for guild in bot.guilds]}")


def run_discord_bot():
    try:
        bot.run(os.environ['DISCORD_BOT_TOKEN'])
    except Exception as e:
        print(f"Error starting the bot: {e}")


# Keep Flask alive and start the bot
keep_alive()
run_discord_bot()
