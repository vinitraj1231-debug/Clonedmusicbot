import asyncio
import os
from yt_dlp import YoutubeDL
import config

ytdl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "geo_bypass": True,
    "nocheckcertificate": True,
    "quiet": True,
    "no_warnings": True,
    "extract_flat": "in_playlist",
    "cachedir": False,
}

if os.path.exists(config.YT_COOKIES_PATH):
    ytdl_opts["cookiefile"] = config.YT_COOKIES_PATH

class YoutubeExtractor:
    def __init__(self):
        self.ytdl = YoutubeDL(ytdl_opts)

    async def extract_info(self, url: str):
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
        except Exception as e:
            return {"error": str(e)}

    async def get_stream_url(self, url: str):
        info = await self.extract_info(url)
        if "error" in info:
            # Fallback for search
            if "ytsearch" not in url:
                return await self.get_stream_url(f"ytsearch:{url}")
            return None, info["error"]

        if "entries" in info:
            info = info["entries"][0]

        formats = info.get("formats", [])
        for f in formats:
            if f.get("acodec") != "none" and f.get("vcodec") == "none":
                return f["url"], info

        return info.get("url"), info

extractor = YoutubeExtractor()
