from pyrogram import filters, Client
from pyrogram.types import Message
from bot.helpers.playback import play_logic
import config

@Client.on_message(filters.command(["play", "p"], prefixes=config.PREFIXES) & filters.group)
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Give me a song name or link!")

    query = " ".join(message.command[1:])
    await play_logic(message, query)

@Client.on_message(filters.command(["skip", "next"], prefixes=config.PREFIXES) & filters.group)
async def skip_command(client: Client, message: Message):
    from bot.core.client import core
    from bot.database.cache import cache
    from bot.core.extractor import extractor
    from pytgcalls.types.stream import MediaStream, AudioQuality, VideoQuality

    chat_id = message.chat.id
    queue = await cache.get_queue(chat_id)

    if len(queue) > 1:
        queue.pop(0)
        await cache.set_queue(chat_id, queue)
        next_song = queue[0]

        m = await message.reply_text(f"Skipping... Next: **{next_song['title']}**")

        stream_url, _ = await extractor.get_stream_url(next_song["link"])
        if not stream_url:
            return await m.edit("Failed to get stream URL for next song.")

        if next_song.get("video"):
            stream = MediaStream(stream_url, video_parameters=VideoQuality.HD_720p)
        else:
            stream = MediaStream(stream_url, audio_parameters=AudioQuality.HIGH)

        await core.call.play(chat_id, stream)
        await m.edit(f"Skipped! Now playing: **{next_song['title']}**")
    else:
        await cache.clear_queue(chat_id)
        try:
            await core.call.leave_call(chat_id)
        except:
            pass
        await message.reply_text("Queue empty, leaving voice chat.")

@Client.on_message(filters.command(["stop", "end"], prefixes=config.PREFIXES) & filters.group)
async def stop_command(client: Client, message: Message):
    from bot.core.client import core
    from bot.database.cache import cache

    chat_id = message.chat.id
    await cache.clear_queue(chat_id)
    try:
        await core.call.leave_call(chat_id)
    except:
        pass
    await message.reply_text("Playback stopped.")
