import logging
from pyrogram import Client
from pytgcalls import PyTgCalls
import config

LOGGER = logging.getLogger("SupremeCore")

class SupremeCore:
    def __init__(self):
        self.bot = Client(
            "SupremeBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="bot/plugins"),
        )
        self.assistant = Client(
            "SupremeAssistant",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.STRING_SESSION,
        )
        self.call = PyTgCalls(self.assistant)
        self.clones = {} # To keep track of running clone clients

    async def stop_all(self):
        try:
            await self.call.stop()
        except:
            pass
        try:
            await self.bot.stop()
        except:
            pass
        try:
            await self.assistant.stop()
        except:
            pass

core = SupremeCore()
