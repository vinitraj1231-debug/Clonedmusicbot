from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.database.db import db
from bot.core.client import core
import config

@Client.on_message(filters.command("admin") & filters.user(config.OWNER_ID))
async def admin_panel(client: Client, message: Message):
    buttons = [
        [
            InlineKeyboardButton("Assistant Settings", callback_data="admin_assistant"),
            InlineKeyboardButton("Bot Settings", callback_data="admin_bot"),
        ],
        [
            InlineKeyboardButton("Global Stats", callback_data="admin_stats"),
            InlineKeyboardButton("Clone System", callback_data="admin_clones"),
        ],
        [
            InlineKeyboardButton("Sudo Users", callback_data="admin_sudos"),
            InlineKeyboardButton("Banned Users", callback_data="admin_banned"),
        ],
        [
            InlineKeyboardButton("Close", callback_data="admin_close"),
        ]
    ]
    await message.reply_text(
        "⚡ **Supreme Admin Panel**\nEdit everything directly from here.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^admin_"))
async def admin_callback(client: Client, query: CallbackQuery):
    data = query.data.split("_")[1]

    if data == "assistant":
        buttons = [
            [InlineKeyboardButton("Change Name", callback_data="set_ast_name")],
            [InlineKeyboardButton("Change Bio", callback_data="set_ast_bio")],
            [InlineKeyboardButton("Back", callback_data="admin_main")],
        ]
        await query.message.edit("Assistant Settings:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "stats":
        clones_count = await db.clones.count_documents({})
        users_count = await db.users.count_documents({})
        msg = f"📊 **Global Statistics**\n\nTotal Users: {users_count}\nTotal Clones: {clones_count}\nActive Sessions: {len(core.clones) + 1}"
        await query.message.edit(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="admin_main")]]))

    elif data == "main":
        buttons = [
            [
                InlineKeyboardButton("Assistant Settings", callback_data="admin_assistant"),
                InlineKeyboardButton("Bot Settings", callback_data="admin_bot"),
            ],
            [
                InlineKeyboardButton("Global Stats", callback_data="admin_stats"),
                InlineKeyboardButton("Clone System", callback_data="admin_clones"),
            ],
            [
                InlineKeyboardButton("Sudo Users", callback_data="admin_sudos"),
                InlineKeyboardButton("Banned Users", callback_data="admin_banned"),
            ],
            [
                InlineKeyboardButton("Close", callback_data="admin_close"),
            ]
        ]
        await query.message.edit("⚡ **Supreme Admin Panel**", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "close":
        await query.message.delete()

@Client.on_callback_query(filters.regex("^set_ast_"))
async def set_ast_callback(client: Client, query: CallbackQuery):
    action = query.data.split("_")[2]

    if action == "name":
        # In a real bot, we'd use a conversation handler or expect next message
        await query.answer("Send the new name for the assistant.", show_alert=True)
    elif action == "bio":
        await query.answer("Send the new bio for the assistant.", show_alert=True)
