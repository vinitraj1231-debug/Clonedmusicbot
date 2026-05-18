from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import config

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    await message.reply_text(
        f"Hello {message.from_user.mention}!\n\nI am {config.BOT_NAME}, a futuristic VC Music Bot.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Add to Group", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true"),
            ],
            [
                InlineKeyboardButton("Support", url=config.SUPPORT_GROUP),
                InlineKeyboardButton("Channel", url=config.SUPPORT_CHANNEL),
            ],
            [
                InlineKeyboardButton("Commands", callback_data="help_cmds"),
            ]
        ])
    )

@Client.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    await message.reply_text("Pong! 🏓")
