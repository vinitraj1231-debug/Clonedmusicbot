import os
import sys
from dotenv import load_dotenv

load_dotenv()

def get_int_env(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

# Essential Variables
API_ID = get_int_env("API_ID", 0)
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
STRING_SESSION = os.getenv("STRING_SESSION", "")
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "")

if not (API_ID and API_HASH and BOT_TOKEN and STRING_SESSION and MONGO_DB_URI):
    print("CRITICAL: Missing essential environment variables (API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, MONGO_DB_URI)")
    # We don't exit here to allow Docker/Render to show the error in logs properly,
    # but the bot will fail later during startup.

REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379")

OWNER_ID = get_int_env("OWNER_ID", 0)
LOG_GROUP_ID = get_int_env("LOG_GROUP_ID", 0)

SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/DevilsHeavenMF")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/DevilsHeavenMF")

BOT_NAME = os.getenv("BOT_NAME", "Supreme Music")
ALIVE_IMAGE = os.getenv("ALIVE_IMAGE", "https://telegra.ph/file/default.jpg")
START_IMAGE = os.getenv("START_IMAGE", "https://telegra.ph/file/default.jpg")
THUMBNAIL = os.getenv("THUMBNAIL", "https://telegra.ph/file/default.jpg")

AUTO_LEAVE = get_int_env("AUTO_LEAVE", 3600)
AUTO_RESTART = os.getenv("AUTO_RESTART", "True").lower() == "true"
MAX_QUALITY = os.getenv("MAX_QUALITY", "high")
YT_COOKIES_PATH = os.getenv("YT_COOKIES_PATH", "cookies.txt")

# Default Prefixes
PREFIXES = os.getenv("PREFIXES", "/ ! .").split()

# Constants
SUDO_USERS = [OWNER_ID]
