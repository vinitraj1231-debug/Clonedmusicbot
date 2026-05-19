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
        LOGGER.info("Stopping all clients...")

        # Stop clones
        for user_id, client in self.clones.items():
            try:
                await client.stop()
                LOGGER.info(f"Stopped clone for user {user_id}")
            except Exception as e:
                LOGGER.error(f"Error stopping clone for user {user_id}: {e}")

        # Stop PyTgCalls
        try:
            await self.call.stop()
            LOGGER.info("Stopped PyTgCalls")
        except Exception as e:
            LOGGER.error(f"Error stopping PyTgCalls: {e}")

        # Stop Assistant
        try:
            await self.assistant.stop()
            LOGGER.info("Stopped Assistant")
        except Exception as e:
            LOGGER.error(f"Error stopping Assistant: {e}")

        # Stop Bot
        try:
            await self.bot.stop()
            LOGGER.info("Stopped Bot")
        except Exception as e:
            LOGGER.error(f"Error stopping Bot: {e}")

core = SupremeCore()
