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
batch_notifications = {}  # Dictionary to store batch notifications


# Startup Logging
print("Attempting to start the bot...")


@bot.event
async def on_ready():
    print("Bot has successfully started!")
    print(f"Logged in as: {bot.user}")
    print(f"Connected to guilds: {[guild.name for guild in bot.guilds]}")


@bot.event
async def on_voice_state_update(member, before, after):
    print(f"Voice state update detected for {member.name}")
    if before.channel is None and after.channel is not None:  # User joins a voice channel
        print(f"{member.name} joined {after.channel.name}")
        guild = member.guild
        notification_channel = discord.utils.get(
            guild.text_channels, name=NOTIFICATION_CHANNEL_NAME)

        if not notification_channel:
            print(f"Notification channel '{NOTIFICATION_CHANNEL_NAME}' not found.")
            return

        # Add user to the batch notifications for this guild
        if guild.id not in batch_notifications:
            batch_notifications[guild.id] = []
        batch_notifications[guild.id].append(f"{member.name} joined {after.channel.name}")

        # Process batch notifications with a delay
        await process_notifications(guild, notification_channel)


async def process_notifications(guild, notification_channel):
    await asyncio.sleep(5)  # Wait 5 seconds to collect all join events
    if guild.id in batch_notifications and batch_notifications[guild.id]:
        try:
            # Combine all notifications into one message
            combined_message = "\n".join(batch_notifications[guild.id])
            print(f"Sending notifications:\n{combined_message}")
            await notification_channel.send(combined_message)
            print(f"Notifications sent successfully for guild {guild.id}")
            batch_notifications[guild.id] = []  # Clear batch after sending
        except discord.errors.HTTPException as e:
            print(f"Rate limit hit: {e}")
        except Exception as e:
            print(f"Error while sending notifications: {e}")


# Keep Flask alive and start the bot
keep_alive()
bot.run(os.environ['DISCORD_BOT_TOKEN'])
