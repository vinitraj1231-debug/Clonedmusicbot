from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from bs4 import BeautifulSoup

@Client.on_message(filters.command("lyrics"))
async def get_lyrics(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/lyrics SONG_NAME`")

    query = " ".join(message.command[1:])
    m = await message.reply_text("Searching lyrics...")

    # Very basic search logic for demonstration
    async with aiohttp.ClientSession() as session:
        search_url = f"https://www.google.com/search?q={query}+lyrics"
        async with session.get(search_url) as resp:
            if resp.status == 200:
                text = await resp.text()
                # In a real app, you'd use a proper lyrics API (like Genius or Musixmatch)
                await m.edit(f"Lyrics for **{query}** not found (API required for accuracy).")
            else:
                await m.edit("Failed to fetch lyrics.")
