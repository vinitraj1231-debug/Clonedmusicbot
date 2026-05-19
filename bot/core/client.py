import logging
import asyncio
from pyrogram import Client
import pyrogram.errors

# Monkeypatch GroupcallForbidden for pytgcalls compatibility
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(Exception):
        pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden

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

    async def start_client(self, client: Client):
        while True:
            try:
                await client.start()
                break
            except pyrogram.errors.FloodWait as e:
                LOGGER.warning(f"FloodWait: Waiting for {e.value} seconds before retrying...")
                await asyncio.sleep(e.value)
            except Exception as e:
                LOGGER.error(f"Failed to start client: {e}")
                raise e

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
