from motor.motor_asyncio import AsyncIOMotorClient
import config

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGO_DB_URI)
        self.db = self.client["SupremeMusic"]
        self.users = self.db["users"]
        self.chats = self.db["chats"]
        self.clones = self.db["clones"]
        self.settings = self.db["settings"]

    # --- User Management ---
    async def is_sudo(self, user_id: int):
        if user_id in config.SUDO_USERS:
            return True
        user = await self.users.find_one({"user_id": user_id})
        return user.get("is_sudo", False) if user else False

    async def add_sudo(self, user_id: int):
        await self.users.update_one({"user_id": user_id}, {"$set": {"is_sudo": True}}, upsert=True)

    async def remove_sudo(self, user_id: int):
        await self.users.update_one({"user_id": user_id}, {"$set": {"is_sudo": False}}, upsert=True)

    # --- Chat Settings ---
    async def get_chat_settings(self, chat_id: int):
        settings = await self.chats.find_one({"chat_id": chat_id})
        if not settings:
            settings = {
                "chat_id": chat_id,
                "loop": 0,
                "quality": "high",
                "autoplay": False,
                "prefix": "/",
            }
            await self.chats.insert_one(settings)
        return settings

    async def set_chat_setting(self, chat_id: int, key: str, value):
        await self.chats.update_one({"chat_id": chat_id}, {"$set": {key: value}}, upsert=True)

    # --- Global Settings (Admin Panel) ---
    async def get_global_settings(self):
        settings = await self.settings.find_one({"id": "GLOBAL"})
        if not settings:
            settings = {
                "id": "GLOBAL",
                "assistant_name": config.BOT_NAME,
                "maintenance": False,
                "clone_system": True,
            }
            await self.settings.insert_one(settings)
        return settings

    async def update_global_setting(self, key: str, value):
        await self.settings.update_one({"id": "GLOBAL"}, {"$set": {key: value}}, upsert=True)

db = Database()
