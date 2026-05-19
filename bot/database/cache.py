import redis.asyncio as redis
import config
import json

import logging

LOGGER = logging.getLogger("Cache")

class Cache:
    def __init__(self):
        self.redis = redis.from_url(config.REDIS_URI, decode_responses=True)

    async def ping(self):
        try:
            await self.redis.ping()
            LOGGER.info("Successfully connected to Redis.")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to connect to Redis: {e}")
            return False

    async def set_queue(self, chat_id: int, queue: list):
        await self.redis.set(f"queue:{chat_id}", json.dumps(queue))

    async def get_queue(self, chat_id: int):
        data = await self.redis.get(f"queue:{chat_id}")
        return json.loads(data) if data else []

    async def clear_queue(self, chat_id: int):
        await self.redis.delete(f"queue:{chat_id}")

cache = Cache()
