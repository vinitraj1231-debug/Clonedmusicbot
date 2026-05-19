from bot.database.cache import cache
import logging

LOGGER = logging.getLogger("QueueManager")

async def add_to_queue(chat_id, title, duration, link, thumb, user_id, user_name):
    queue = await cache.get_queue(chat_id)
    item = {
        "title": title,
        "duration": duration,
        "link": link,
        "thumb": thumb,
        "user_id": user_id,
        "user_name": user_name,
    }
    queue.append(item)
    await cache.set_queue(chat_id, queue)
    return len(queue)

async def get_next_song(chat_id):
    queue = await cache.get_queue(chat_id)
    if len(queue) > 1:
        queue.pop(0)
        await cache.set_queue(chat_id, queue)
        return queue[0]
    return None
