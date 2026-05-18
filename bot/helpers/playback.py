from pyrogram.types import Message
from bot.core.extractor import extractor
from bot.helpers.queues import add_to_queue
from bot.core.client import core
from pytgcalls.types.stream import MediaStream, AudioQuality, VideoQuality
import config

async def play_logic(message: Message, query: str, video: bool = False):
    chat_id = message.chat.id
    user_id = message.from_user.id

    m = await message.reply_text("Searching...")

    if not (query.startswith("http") or query.startswith("www")):
        query = f"ytsearch:{query}"

    stream_url, info = await extractor.get_stream_url(query)

    if not stream_url:
        return await m.edit(f"Failed to find results: {info}")

    title = info.get("title", "Unknown")
    duration = info.get("duration", 0)
    thumb = info.get("thumbnail", config.THUMBNAIL)

    pos = await add_to_queue(chat_id, title, duration, stream_url, thumb, user_id, message.from_user.first_name)

    if pos == 1:
        try:
            if video:
                stream = MediaStream(stream_url, video_parameters=VideoQuality.HD_720p)
            else:
                stream = MediaStream(stream_url, audio_parameters=AudioQuality.HIGH)
            await core.call.play(chat_id, stream)
            await m.edit(f"Playing **{title}**")
        except Exception as e:
            await m.edit(f"Error: {e}")
    else:
        await m.edit(f"Added to queue at position {pos-1}\n**{title}**")
