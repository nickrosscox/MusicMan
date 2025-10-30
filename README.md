# MusicMan Discord Bot 🎵

A simple, lag-free Discord music bot that streams music directly from YouTube.

## Features

- 🎵 Stream music from YouTube
- ⚡ Optimized for minimal lag
- 🎮 Simple slash commands
- 📝 Queue management
- ⏸️ Playback controls (pause, resume, skip)

## Commands

- `/join` - Join your voice channel
- `/play <url>` - Play a song from YouTube
- `/pause` - Pause the current song
- `/resume` - Resume playback
- `/skip` - Skip to the next song
- `/stop` - Stop playing and clear the queue
- `/queue` - Show the current queue
- `/leave` - Leave the voice channel

## Prerequisites

- Python 3.10 or higher
- FFmpeg installed on your system
- Discord Bot Token

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/MusicMan.git
cd MusicMan
```

### 2. Create a virtual environment

```bash
python -m venv discord_bot_env
```

### 3. Activate the virtual environment

**Windows:**
```bash
discord_bot_env\Scripts\activate
```

**Linux/Mac:**
```bash
source discord_bot_env/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install FFmpeg

**Windows:**
- Download from [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
- Extract to `C:\ffmpeg`
- Add `C:\ffmpeg\bin` to your PATH

**Mac:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

### 6. Set up your Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" tab and create a bot
4. Enable these Privileged Gateway Intents:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
5. Copy your bot token
6. Go to OAuth2 → URL Generator
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Connect`, `Speak`, `Use Voice Activity`, `Send Messages`, `Read Message History`
7. Use the generated URL to invite the bot to your server

### 7. Configure the bot

Create a `.env` file in the project directory:

```bash
DISCORD_BOT_TOKEN=your_bot_token_here
```

### 8. Run the bot

```bash
python music_bot.py
```

You should see:
```
🤖 Starting Discord Music Bot...
✅ Bot is ready! Logged in as MusicMan#XXXX
📊 Connected to X server(s)
🔄 Synced 8 command(s)
```

## Usage

1. Join a voice channel in your Discord server
2. Use `/join` to make the bot join your channel
3. Use `/play <youtube_url>` to play music
4. Enjoy! 🎶

## Troubleshooting

### Bot won't connect to voice channel
- Make sure FFmpeg is installed and in your PATH
- Verify the bot has proper permissions in your Discord server
- Check that you've enabled the Server Members Intent in the Developer Portal

### Audio is laggy
- Check your internet connection
- Try using a different voice server region in Discord server settings

### Commands not showing up
- Make sure you've invited the bot with `applications.commands` scope
- Wait a few minutes for Discord to sync the commands
- Try kicking and re-inviting the bot

## Contributing

Feel free to fork this project and submit pull requests!

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube integration
- Powered by FFmpeg for audio processing