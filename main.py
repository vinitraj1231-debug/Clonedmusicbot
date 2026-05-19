import asyncio
import logging
import signal
import os
from aiohttp import web
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

class HealthServer:
    def __init__(self):
        self.runner = None

    async def start(self):
        app = web.Application()
        app.router.add_get("/", self.health_check)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        port = int(os.getenv("PORT", 8080))
        site = web.TCPSite(self.runner, "0.0.0.0", port)
        await site.start()
        LOGGER.info(f"Health check server started on port {port}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
            LOGGER.info("Health check server stopped.")

    async def health_check(self, request):
        return web.Response(text="Supreme Music Bot is running!")

health_server = HealthServer()

async def shutdown(stop_event, signal=None):
    if signal:
        LOGGER.info(f"Received exit signal {signal.name}...")

    LOGGER.info("Shutting down bot...")
    stop_event.set()

async def main():
    LOGGER.info("Starting Supreme Music Bot...")

    # Verify Database Connection
    if not await db.ping():
        LOGGER.critical("Could not connect to MongoDB. Please check MONGO_DB_URI.")
        return

    # Verify Redis Connection
    if not await cache.ping():
        LOGGER.critical("Could not connect to Redis. Please check REDIS_URI.")
        return

    # Start Health Check Server for Render
    await health_server.start()

    # PyTgCalls event handler (Register before starting call)
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
                    try:
                        await core.call.play(chat_id, MediaStream(next_song["link"], audio_parameters=AudioQuality.HIGH))
                    except Exception as e:
                        LOGGER.error(f"Error playing next song in {chat_id}: {e}")
                        await core.call.leave_call(chat_id)
                else:
                    await core.call.leave_call(chat_id)
            else:
                await core.call.leave_call(chat_id)
        except Exception as e:
            LOGGER.error(f"Error in stream_end_handler for {chat_id}: {e}")

    try:
        await core.start_client(core.bot)
        await core.start_client(core.assistant)
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

    await health_server.stop()
    await core.stop_all()

if __name__ == "__main__":
    try:
        # Create downloads directory if not exists
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        LOGGER.exception("Fatal error during execution")
