import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")
STAFF_CHANNEL_ID = int(os.getenv("STAFF_CHANNEL_ID"))

# Set up logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_logs.log"),  # Log file
        logging.StreamHandler()               # Console output
    ]
)

ALLOWED_CHANNELS = [12345678,23456789] # you can use many channels. 

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# User warning and mute tracking
user_warnings = {}
MESSAGE_THRESHOLD = 5  # Number of messages in 5 seconds that constitutes spam
TIME_WINDOW = 5  # Time in seconds to count messages
WARNING_RESET_TIME = 10  # Seconds before warnings reset if user stops spamming

@bot.event
async def on_ready():
    logging.info(f"{bot.user} is online and ready!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if message is in an allowed channel
    if message.channel.id not in ALLOWED_CHANNELS:
        logging.info(f"Message in {message.channel.name} ignored (not an allowed channel).")
        return

    # Initialize or update user warnings
    user_id = message.author.id
    current_time = datetime.now()

    if user_id not in user_warnings:
        user_warnings[user_id] = {'count': 0, 'timestamps': []}

    # Remove timestamps older than TIME_WINDOW
    user_warnings[user_id]['timestamps'] = [
        timestamp for timestamp in user_warnings[user_id]['timestamps']
        if (current_time - timestamp).total_seconds() <= TIME_WINDOW
    ]

    # Add the new message timestamp
    user_warnings[user_id]['timestamps'].append(current_time)

    # Check if user has reached the message threshold
    if len(user_warnings[user_id]['timestamps']) >= MESSAGE_THRESHOLD:
        user_warnings[user_id]['count'] += 1
        user_warnings[user_id]['timestamps'] = []  # Reset timestamps after threshold is reached

        if user_warnings[user_id]['count'] == 1:
            await message.channel.send(f"{message.author.display_name}, Warning 1/3 for spamming.")
            logging.warning(f"Warning 1 for user {message.author.display_name} (ID: {user_id}) in {message.channel.name}")
        elif user_warnings[user_id]['count'] == 2:
            await message.channel.send(f"{message.author.display_name}, Warning 2/3 for spamming.")
            logging.warning(f"Warning 2 for user {message.author.display_name} (ID: {user_id}) in {message.channel.name}")
        elif user_warnings[user_id]['count'] >= 3:
            # Mute the user by disabling the send messages permission
            try:
                await message.channel.set_permissions(message.author, send_messages=False)
                await message.channel.send(f"{message.author.display_name}, Warning 3/3. You have been muted for spamming.")
                logging.warning(f"User {message.author.display_name} (ID: {user_id}) muted for spamming in {message.channel.name}")
                
                # Log mute action in staff channel
                log_channel = bot.get_channel(STAFF_CHANNEL_ID)
                if log_channel:
                    await log_channel.send(f"User {message.author.display_name} has been muted for spamming in {message.channel.mention} (Time: {current_time.strftime('%H:%M')} Date: {current_time.strftime('%Y-%m-%d')})")

                # Schedule automatic unmute after 1 hour
                await asyncio.sleep(3600)
                await message.channel.set_permissions(message.author, overwrite=None)
                
                # Notify user and staff of unmute
                await message.channel.send(f"{message.author.display_name}, your mute has been removed.")
                if log_channel:
                    await log_channel.send(f"User {message.author.display_name} has been unmuted automatically after 1 hour.")
                logging.info(f"User {message.author.display_name} (ID: {user_id}) unmuted automatically after 1 hour.")

            except discord.Forbidden:
                logging.error(f"Permission error: Could not mute {message.author}.")
            
            # Reset user's warnings after muting
            user_warnings[user_id] = {'count': 0, 'timestamps': []}

    # Reset warnings if no spam detected within WARNING_RESET_TIME
    else:
        last_message_time = user_warnings[user_id]['timestamps'][-1]
        if (current_time - last_message_time).total_seconds() > WARNING_RESET_TIME:
            user_warnings[user_id] = {'count': 0, 'timestamps': []}

    await bot.process_commands(message)

bot.run(TOKEN)
