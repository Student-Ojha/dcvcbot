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


# Bot setup with intents
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


@bot.event
async def on_voice_state_update(member, before, after):
    print(f"Voice state updated for {member.name}: Before: {before.channel}, After: {after.channel}")

    if before.channel is None and after.channel is not None:  # User joined a voice channel
        print(f"{member.name} joined {after.channel.name}")
        guild = member.guild
        notification_channel = discord.utils.get(
            guild.text_channels, name=NOTIFICATION_CHANNEL_NAME)

        if not notification_channel:
            print(f"Notification channel '{NOTIFICATION_CHANNEL_NAME}' not found.")
            return

        try:
            await notification_channel.send(f"{member.name} joined {after.channel.name}")
            print(f"Notification sent for {member.name}")
        except Exception as e:
            print(f"Failed to send notification: {e}")


def run_discord_bot():
    try:
        print("Starting Discord bot...")
        bot.run(os.environ['DISCORD_BOT_TOKEN'])
    except discord.LoginFailure:
        print("Invalid token. Please check your DISCORD_BOT_TOKEN.")
    except Exception as e:
        print(f"Error starting the bot: {e}")


# Keep Flask alive and start the bot
keep_alive()
run_discord_bot()
