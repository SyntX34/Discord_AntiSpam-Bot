Mutes user if he sends too many messages inside 5 seconds then 1st warning, if he continues give another warning and if he still doesn't stop, 3rd warning and instantly mute for 1 hour. He will be only able to view channel and react on other people texts. After 1 hour, his mutes will be automatically removed.

Suppose if a user has gotten 2 warnings and he decides not to send any texts for 10 seconds then his warnings will be resetted.

It also send logs to Staff Channels.

Also you can add multiple channels, this bot will only look for spam messages in those channel.

Dependencies:

- Discord
- asyncio
- os
- dotenv


Make sure you have these packages before running it.

To install these packages, run these commands:
- pip install discord.py
- pip install python-dotenv

Installation (Linux): 
- git clone https://github.com/SyntX34/Discord_AntiSpam-Bot.git
- cd Discord_AntiSpam-Bot
- sudo chmod +x main.py
- sudo nano .env (edit stuffs)
- python3 main.py
