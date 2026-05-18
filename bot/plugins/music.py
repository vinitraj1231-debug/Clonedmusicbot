from pyrogram import filters, Client
from pyrogram.types import Message
from bot.helpers.playback import play_logic
import config

@Client.on_message(filters.command(["play", "p"]) & filters.group)
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Give me a song name or link!")

    query = " ".join(message.command[1:])
    await play_logic(message, query)

@Client.on_message(filters.command(["skip", "next"]) & filters.group)
async def skip_command(client: Client, message: Message):
    from bot.core.client import core
    from bot.database.cache import cache
    from pytgcalls.types.stream import AudioPiped

    chat_id = message.chat.id
    queue = await cache.get_queue(chat_id)

    if len(queue) > 1:
        queue.pop(0)
        await cache.set_queue(chat_id, queue)
        next_song = queue[0]
        await core.call.change_stream(chat_id, AudioPiped(next_song["link"]))
        await message.reply_text(f"Skipped! Now playing: **{next_song['title']}**")
    else:
        await cache.clear_queue(chat_id)
        try:
            await core.call.leave_group_call(chat_id)
        except:
            pass
        await message.reply_text("Queue empty, leaving voice chat.")

@Client.on_message(filters.command(["stop", "end"]) & filters.group)
async def stop_command(client: Client, message: Message):
    from bot.core.client import core
    from bot.database.cache import cache

    chat_id = message.chat.id
    await cache.clear_queue(chat_id)
    try:
        await core.call.leave_group_call(chat_id)
    except:
        pass
    await message.reply_text("Playback stopped.")
