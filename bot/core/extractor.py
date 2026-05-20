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
    "source_address": "0.0.0.0", # Bind to ipv4 since ipv6 can cause issues
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
    }
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
        if not info or "error" in info:
            # Fallback for search
            if url and "ytsearch" not in url and not (url.startswith("http") or url.startswith("www")):
                return await self.get_stream_url(f"ytsearch:{url}")
            return None, info.get("error", "Unknown extraction error")

        if "entries" in info:
            info = info["entries"][0]

        formats = info.get("formats", [])
        for f in formats:
            if f.get("acodec") != "none" and f.get("vcodec") == "none":
                return f["url"], info

        return info.get("url"), info

extractor = YoutubeExtractor()
