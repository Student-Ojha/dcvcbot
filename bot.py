import discord
from discord.ext import commands
from time import time
from flask import Flask
from threading import Thread
import os
import asyncio  # Import asyncio for delays

# Web server setup for UptimeRobot to keep the bot alive
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
joined_users = {}  # To batch notifications for users joining simultaneously


@bot.event
async def on_ready():
    print(f"Bot is online and logged in as {bot.user}")


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:  # User joined a voice channel
        guild = member.guild
        notification_channel = discord.utils.get(
            guild.text_channels, name=NOTIFICATION_CHANNEL_NAME)

        # Add the member to the joined_users dictionary for batching
        if guild.id not in joined_users:
            joined_users[guild.id] = []
        joined_users[guild.id].append((member.name, after.channel.name))

        # Wait 5 seconds to batch notifications
        await asyncio.sleep(5)

        # Combine all notifications for the guild
        if guild.id in joined_users and notification_channel:
            try:
                # Create a combined message for all users
                messages = [
                    f"{user} joined {channel}"
                    for user, channel in joined_users[guild.id]
                ]
                combined_message = "\n".join(messages)

                # Send the combined notification
                await notification_channel.send(combined_message)
                joined_users[guild.id] = []  # Clear the list after sending
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
