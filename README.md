# 🚀 Supreme VC Music Bot

The most advanced Telegram Voice Chat Music Bot with a futuristic architecture, modular plugin system, and ultra-advanced clone system.

## ✨ Features

- **Multi-Group Playback**: Stream music in unlimited groups simultaneously.
- **Ultra-Advanced Clone System**: Users can create their own bot instances via `/clone`.
- **Supreme Admin Panel**: Full control over the bot directly from Telegram.
- **Futuristic UI/UX**: Neon-themed interface with dynamic progress bars.
- **Stable Playback**: Powered by `PyTgCalls` and `FFmpeg` with auto-reconnect.
- **Modular Architecture**: Easy to extend and add new plugins.
- **Persistence**: All clones and settings are saved in MongoDB and Redis.

## 🛠️ Setup & Deployment

### 1. Requirements
- Python 3.11+
- MongoDB
- Redis
- FFmpeg

### 2. Environment Variables
Create a `.env` file or set the following variables:
- `API_ID`: Your Telegram API ID.
- `API_HASH`: Your Telegram API Hash.
- `BOT_TOKEN`: Your main bot token.
- `STRING_SESSION`: Pyrogram string session for the assistant.
- `MONGO_DB_URI`: MongoDB connection string.
- `REDIS_URI`: Redis connection string.
- `OWNER_ID`: Your Telegram User ID.

### 3. Local Installation
```bash
git clone https://github.com/yourrepo/SupremeBot
cd SupremeBot
pip install -r requirements.txt
python main.py
```

### 4. Docker Deployment
```bash
docker build -t supreme-bot .
docker run -d supreme-bot
```

## 📜 Commands

### Public
- `/play [name/link]` - Play a song.
- `/skip` - Skip current song.
- `/stop` - Stop playback.
- `/queue` - View current queue.
- `/download [name]` - Download a song.

### Private
- `/start` - Start the bot.
- `/clone [token]` - Clone the bot.

### Admin
- `/admin` - Open the Supreme Admin Panel.
- `/clones` - List all active clones.

## 🤝 Support
Join our [Support Group](https://t.me/DevilsHeavenMF) for help and updates.
