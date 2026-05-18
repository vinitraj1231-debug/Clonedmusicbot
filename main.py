import asyncio
from bot.core.client import core
from pytgcalls.types import Update
from pytgcalls.types.stream import AudioPiped
from bot.database.cache import cache
from bot.database.db import db
from bot.plugins.clones import start_clone
import logging

LOGGER = logging.getLogger("Main")

async def main():
    LOGGER.info("Starting Supreme Music Bot...")
    await core.bot.start()
    await core.assistant.start()
    await core.call.start()

    # Start saved clones
    clones = await db.clones.find().to_list(None)
    for clone in clones:
        asyncio.create_task(start_clone(clone["user_id"], clone["bot_token"]))

    # PyTgCalls event handler
    @core.call.on_stream_end()
    async def stream_end_handler(client, update: Update):
        chat_id = update.chat_id
        queue = await cache.get_queue(chat_id)
        if queue:
            queue.pop(0)
            await cache.set_queue(chat_id, queue)
            if queue:
                next_song = queue[0]
                await core.call.change_stream(chat_id, AudioPiped(next_song["link"]))
            else:
                try:
                    await core.call.leave_group_call(chat_id)
                except:
                    pass
        else:
            try:
                await core.call.leave_group_call(chat_id)
            except:
                pass

    bot_me = await core.bot.get_me()
    assistant_me = await core.assistant.get_me()

    LOGGER.info(f"Bot started as {bot_me.first_name}")
    LOGGER.info(f"Assistant started as {assistant_me.first_name}")

    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
