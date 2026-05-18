from pytgcalls import PyTgCalls
from pytgcalls.types import StreamEnded
from pytgcalls.types.stream import MediaStream, AudioQuality, VideoQuality
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
        try:
            await self.call.start()
            LOGGER.info("PyTgCalls started successfully.")
        except Exception as e:
            LOGGER.error(f"Failed to start PyTgCalls: {e}")

    async def join_call(self, chat_id: int, stream_url: str, video: bool = False):
        try:
            if video:
                stream = MediaStream(stream_url, video_parameters=VideoQuality.HD_720p)
            else:
                stream = MediaStream(stream_url, audio_parameters=AudioQuality.HIGH)

            await self.call.play(chat_id, stream)
            LOGGER.info(f"Joined call in {chat_id} with {'video' if video else 'audio'}")
            return True
        except Exception as e:
            LOGGER.error(f"Error joining call in {chat_id}: {e}")
            return False

    async def leave_call(self, chat_id: int):
        try:
            await self.call.leave_call(chat_id)
            await cache.clear_queue(chat_id)
            LOGGER.info(f"Left call and cleared queue in {chat_id}")
        except Exception as e:
            LOGGER.error(f"Error leaving call in {chat_id}: {e}")

    async def change_stream(self, chat_id: int, stream_url: str, video: bool = False):
        try:
            if video:
                stream = MediaStream(stream_url, video_parameters=VideoQuality.HD_720p)
            else:
                stream = MediaStream(stream_url, audio_parameters=AudioQuality.HIGH)

            await self.call.play(chat_id, stream)
            LOGGER.info(f"Changed stream in {chat_id}")
        except Exception as e:
            LOGGER.error(f"Error changing stream in {chat_id}: {e}")
