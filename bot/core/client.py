import logging
import asyncio
from pyrogram import Client
import pyrogram.errors

# Monkeypatch GroupcallForbidden for pytgcalls compatibility
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(Exception):
        pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden

import base64
import struct
from pytgcalls import PyTgCalls
import config

LOGGER = logging.getLogger("SupremeCore")

def get_session_string():
    session = config.STRING_SESSION.strip()
    if not session:
        return None

    # Try to decode and check length
    try:
        # Normalize session string: remove all whitespace/newlines that might have been copied
        session = "".join(session.split())

        # Add padding if missing
        padded = session + "=" * (-len(session) % 4)

        try:
            decoded = base64.urlsafe_b64decode(padded)
        except Exception:
            # Fallback to standard base64 if urlsafe fails
            try:
                decoded = base64.b64decode(padded)
            except Exception as e:
                LOGGER.error(f"Failed to decode session string: {e}")
                return session

        LOGGER.info(f"Session string decoded length: {len(decoded)} bytes")

        # Pyrogram v2 session string should be 271 bytes
        if len(decoded) == 271:
            return session

        # v1 (32-bit) is 263 bytes
        # v1 (64-bit) is 267 bytes
        # Sometimes it might be 264 or 268 due to extra padding bytes
        if len(decoded) in [263, 264, 267, 268]:
            LOGGER.info(f"Detected Pyrogram v1 session string ({len(decoded)} bytes). Converting to v2...")
            try:
                if len(decoded) in [263, 264]:
                    # dc_id (B), test_mode (?), auth_key (256s), user_id (I), is_bot (?)
                    dc_id, test_mode, auth_key, user_id, is_bot = struct.unpack(">B?256sI?", decoded[:263])
                else:
                    # dc_id (B), test_mode (?), auth_key (256s), user_id (Q), is_bot (?)
                    dc_id, test_mode, auth_key, user_id, is_bot = struct.unpack(">B?256sQ?", decoded[:267])

                # Pack into v2 format (>BI?256sQ?)
                # dc_id (B), api_id (I), test_mode (?), auth_key (256s), user_id (Q), is_bot (?)
                v2_data = struct.pack(">BI?256sQ?", dc_id, config.API_ID, test_mode, auth_key, user_id, is_bot)
                return base64.urlsafe_b64encode(v2_data).decode().rstrip("=")
            except Exception as e:
                LOGGER.error(f"Error during session conversion: {e}")
                return session

        if len(decoded) != 271:
            LOGGER.warning(f"Session string decodes to {len(decoded)} bytes, but Pyrogram v2 expects 271 bytes. This may fail.")

    except Exception as e:
        LOGGER.error(f"Error while validating session string: {e}")

    return session

class SupremeCore:
    def __init__(self):
        self.bot = Client(
            "SupremeBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="bot/plugins"),
        )
        self.assistant = Client(
            "SupremeAssistant",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=get_session_string(),
        )
        self.call = PyTgCalls(self.assistant)
        self.clones = {} # To keep track of running clone clients

    async def start_client(self, client: Client):
        while True:
            try:
                await client.start()
                break
            except pyrogram.errors.FloodWait as e:
                LOGGER.warning(f"FloodWait: Waiting for {e.value} seconds before retrying...")
                await asyncio.sleep(e.value)
            except Exception as e:
                LOGGER.exception(f"Failed to start client {client.name}: {e}")
                raise e

    async def stop_all(self):
        LOGGER.info("Stopping all clients...")

        # Stop clones
        for user_id, client in self.clones.items():
            try:
                await client.stop()
                LOGGER.info(f"Stopped clone for user {user_id}")
            except Exception as e:
                LOGGER.error(f"Error stopping clone for user {user_id}: {e}")

        # Stop PyTgCalls
        try:
            await self.call.stop()
            LOGGER.info("Stopped PyTgCalls")
        except Exception as e:
            LOGGER.error(f"Error stopping PyTgCalls: {e}")

        # Stop Assistant
        try:
            await self.assistant.stop()
            LOGGER.info("Stopped Assistant")
        except Exception as e:
            LOGGER.error(f"Error stopping Assistant: {e}")

        # Stop Bot
        try:
            await self.bot.stop()
            LOGGER.info("Stopped Bot")
        except Exception as e:
            LOGGER.error(f"Error stopping Bot: {e}")

core = SupremeCore()
