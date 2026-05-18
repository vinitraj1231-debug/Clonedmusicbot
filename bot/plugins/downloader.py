from pyrogram import Client, filters
from pyrogram.types import Message
import os
from yt_dlp import YoutubeDL

@Client.on_message(filters.command(["download", "song"]))
async def download_song(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/download SONG_NAME`")

    query = " ".join(message.command[1:])
    m = await message.reply_text("Downloading...")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "quiet": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]
            file_path = ydl.prepare_filename(info)

        await message.reply_audio(
            audio=file_path,
            title=info.get("title"),
            performer=info.get("uploader"),
            duration=info.get("duration"),
        )
        await m.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        await m.edit(f"Error: {e}")
