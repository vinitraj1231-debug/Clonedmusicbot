import asyncio
import logging
import signal
from bot.core.client import core
from pytgcalls.types import StreamEnded
from pytgcalls.types.stream import MediaStream, AudioQuality
from bot.database.cache import cache
from bot.database.db import db
from bot.plugins.clones import start_clone

# Enhanced Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

LOGGER = logging.getLogger("Main")

async def shutdown(stop_event, signal=None):
    if signal:
        LOGGER.info(f"Received exit signal {signal.name}...")

    LOGGER.info("Shutting down bot...")
    stop_event.set()

async def main():
    LOGGER.info("Starting Supreme Music Bot...")

    try:
        await core.bot.start()
        await core.assistant.start()
        await core.call.start()
    except Exception as e:
        LOGGER.critical(f"Failed to start core components: {e}")
        return

    # Start saved clones
    try:
        clones = await db.clones.find().to_list(None)
        for clone in clones:
            asyncio.create_task(start_clone(clone["user_id"], clone["bot_token"]))
    except Exception as e:
        LOGGER.error(f"Error loading clones: {e}")

    # PyTgCalls event handler
    @core.call.on_update()
    async def stream_end_handler(client, update):
        if not isinstance(update, StreamEnded):
            return

        chat_id = update.chat_id
        try:
            queue = await cache.get_queue(chat_id)
            if queue:
                queue.pop(0)
                await cache.set_queue(chat_id, queue)
                if queue:
                    next_song = queue[0]
                    await core.call.play(chat_id, MediaStream(next_song["link"], audio_parameters=AudioQuality.HIGH))
                else:
                    await core.call.leave_call(chat_id)
            else:
                await core.call.leave_call(chat_id)
        except Exception as e:
            LOGGER.error(f"Error in stream_end_handler for {chat_id}: {e}")

    bot_me = await core.bot.get_me()
    assistant_me = await core.assistant.get_me()

    LOGGER.info(f"Bot started as @{bot_me.username}")
    LOGGER.info(f"Assistant started as {assistant_me.first_name}")

    # Keep the bot running
    stop_event = asyncio.Event()

    # Setup Signal Handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(stop_event, s)))

    await stop_event.wait()

    # Gracefully stop components after wait
    LOGGER.info("Stopping components...")
    try:
        await core.call.stop()
    except:
        pass

    try:
        await core.bot.stop()
    except:
        pass

    try:
        await core.assistant.stop()
    except:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        LOGGER.exception("Fatal error during execution")
