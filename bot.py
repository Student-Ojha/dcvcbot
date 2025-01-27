import discord
from discord.ext import commands
import asyncio
import os
from flask import Flask
from threading import Thread

# Flask app to keep the bot alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

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

NOTIFICATION_CHANNEL_NAME = "vc-notifications"  # Replace with your text channel name

# Store recent joins to prevent duplicate notifications
recent_joins = set()  # A set to track users who recently joined


@bot.event
async def on_ready():
    print(f"Bot has successfully started!")
    print(f"Logged in as: {bot.user}")
    print(f"Connected to guilds: {[guild.name for guild in bot.guilds]}")


@bot.event
async def on_voice_state_update(member, before, after):
    # Ensure this event only triggers when a member joins a voice channel
    if before.channel is None and after.channel is not None:  # User joined a voice channel
        print(f"{member.name} joined {after.channel.name}")

        # Prevent duplicate notifications using a cooldown
        if member.id in recent_joins:
            print(f"Duplicate notification suppressed for {member.name}.")
            return

        # Add user to recent joins with a cooldown
        recent_joins.add(member.id)
        asyncio.get_event_loop().call_later(5, lambda: recent_joins.remove(member.id))  # 5-second cooldown

        # Get the notification channel
        guild = member.guild
        notification_channel = discord.utils.get(
            guild.text_channels, name=NOTIFICATION_CHANNEL_NAME
        )

        if not notification_channel:
            print("Notification channel not found.")
            return

        # Send the notification
        try:
            await notification_channel.send(f"{member.name} joined {after.channel.name}")
            print(f"Notification sent for {member.name}")
        except Exception as e:
            print(f"Failed to send notification: {e}")


async def start_bot():
    retries = 0
    while retries < 5:  # Retry up to 5 times
        try:
            print("Starting Discord bot...")
            await bot.start(os.environ['DISCORD_BOT_TOKEN'])
            break  # Exit loop if successful
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limit
                wait_time = 2 ** retries  # Exponential backoff
                print(f"Rate limited. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                retries += 1
            else:
                print(f"Unexpected error: {e}")
                raise
    else:
        print("Failed to start bot after multiple attempts.")

# Start the keep-alive server
keep_alive()

# Run the bot
asyncio.run(start_bot())
