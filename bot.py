import discord
from discord.ext import commands
from time import time
from flask import Flask
from threading import Thread
import os
import asyncio  # Import asyncio for delays

# Web server setup for Replit to keep the bot alive
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
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Role and channel configurations
NOTIFICATION_CHANNEL_NAME = "vc-notifications"  # Replace with your notification channel name
ROLE_NAME = "VC Notifications"  # Replace with your role name
recent_notifications = {}  # To track recent joins


@bot.event
async def on_ready():
    print(f"Bot is online and logged in as {bot.user}")


@bot.event
async def on_voice_state_update(member, before, after):
    # Check if the user joins a voice channel
    if before.channel is None and after.channel is not None:
        guild = member.guild
        notification_channel = discord.utils.get(
            guild.text_channels, name=NOTIFICATION_CHANNEL_NAME)

        # Cooldown logic: avoid duplicate notifications
        now = time()
        if member.id in recent_notifications:
            last_notification = recent_notifications[member.id]
            if now - last_notification < 30:  # Increased to 30 seconds cooldown
                return
        recent_notifications[member.id] = now

        # Minimalistic notification message
        message = f"{member.name} joined {after.channel.name}."

        # Send the message to the notification channel
        if notification_channel:
            try:
                await notification_channel.send(message)
                await asyncio.sleep(1)  # Add a small delay to avoid rate limits
            except discord.errors.HTTPException as e:
                print(f"Rate limit hit: {e}")
        else:
            print(
                f"Notification channel '{NOTIFICATION_CHANNEL_NAME}' not found."
            )


# Keep the bot alive and run it
keep_alive()
TOKEN = os.environ[
    'DISCORD_BOT_TOKEN']  # Use the environment variable for the token
bot.run(TOKEN)
