from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database.db import db
from bot.core.client import core
import config
import logging

LOGGER = logging.getLogger("CloneSystem")

async def start_clone(user_id, bot_token):
    try:
        new_bot = Client(
            f"clone_{user_id}",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=bot_token,
            plugins=dict(root="bot/plugins"),
        )
        await core.start_client(new_bot)
        core.clones[user_id] = new_bot
        bot_me = await new_bot.get_me()
        LOGGER.info(f"Started clone: @{bot_me.username}")
        return bot_me
    except Exception as e:
        LOGGER.error(f"Failed to start clone for {user_id}: {e}")
        return None

@Client.on_message(filters.command("clone", prefixes=config.PREFIXES) & filters.private)
async def clone_bot(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/clone BOT_TOKEN`")

    bot_token = message.command[1]
    user_id = message.from_user.id

    if user_id in core.clones:
        return await message.reply_text("You already have a running clone. Use /stopclone to stop it first.")

    m = await message.reply_text("Cloning your bot...")

    try:
        bot_me = await start_clone(user_id, bot_token)
        if bot_me:
            # Save to DB for persistence
            await db.clones.update_one(
                {"user_id": user_id},
                {"$set": {"bot_token": bot_token, "bot_username": bot_me.username}},
                upsert=True
            )
            await m.edit(f"Successfully cloned! @{bot_me.username} is now running.")
        else:
            await m.edit("Failed to start the clone. Ensure your bot token is valid and not already in use.")
    except Exception as e:
        LOGGER.error(f"Error in clone_bot command: {e}")
        await m.edit(f"An unexpected error occurred: {e}")

@Client.on_message(filters.command("stopclone", prefixes=config.PREFIXES) & filters.private)
async def stop_clone_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in core.clones:
        return await message.reply_text("You don't have any running clone.")

    m = await message.reply_text("Stopping your clone...")
    try:
        clone_client = core.clones.pop(user_id)
        await clone_client.stop()
        await db.clones.delete_one({"user_id": user_id})
        await m.edit("Successfully stopped and removed your clone.")
    except Exception as e:
        LOGGER.error(f"Error stopping clone: {e}")
        await m.edit(f"Failed to stop clone: {e}")

@Client.on_message(filters.command("clones", prefixes=config.PREFIXES) & filters.user(config.OWNER_ID))
async def list_clones(client: Client, message: Message):
    clones = await db.clones.find().to_list(100)
    if not clones:
        return await message.reply_text("No clones in database.")

    msg = "**Clones in Database:**\n"
    for c in clones:
        status = "✅ Running" if c['user_id'] in core.clones else "❌ Offline"
        msg += f"- @{c['bot_username']} (Owner: {c['user_id']}) - {status}\n"

    await message.reply_text(msg)
