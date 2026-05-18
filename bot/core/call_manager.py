from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.stream import AudioPiped, AudioVideoPiped
from pyrogram import Client
import config
from bot.database.cache import cache
import logging

LOGGER = logging.getLogger("CallManager")

class CallManager:
    def __init__(self, assistant: Client):
        self.call = PyTgCalls(assistant)
        self.assistant = assistant

    async def start(self):
        await self.call.start()

    async def join_call(self, chat_id: int, stream_url: str, video: bool = False):
        try:
            stream = AudioVideoPiped(stream_url) if video else AudioPiped(stream_url)
            await self.call.join_group_call(chat_id, stream)
            return True
        except Exception as e:
            LOGGER.error(f"Error joining call in {chat_id}: {e}")
            return False

    async def leave_call(self, chat_id: int):
        try:
            await self.call.leave_group_call(chat_id)
        except Exception as e:
            LOGGER.error(f"Error leaving call in {chat_id}: {e}")

    async def change_stream(self, chat_id: int, stream_url: str, video: bool = False):
        stream = AudioVideoPiped(stream_url) if video else AudioPiped(stream_url)
        await self.call.change_stream(chat_id, stream)

# In a real app, this would be part of a bigger class
# but for now we define the handler logic here or in plugins.
