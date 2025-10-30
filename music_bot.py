import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import os
from typing import Optional

# ================================
# CONFIGURATION
# ================================

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Replace with your Discord bot token

# ================================
# YT-DLP OPTIONS (Optimized for streaming)
# ================================

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extract_flat': False,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.5"'
}

# ================================
# BOT SETUP
# ================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ================================
# MUSIC QUEUE CLASS
# ================================

class MusicQueue:
    def __init__(self):
        self.queue = []
        self.current = None
        self.voice_client = None

    def add(self, song):
        self.queue.append(song)

    def get_next(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def clear(self):
        self.queue.clear()
        self.current = None

    def is_empty(self):
        return len(self.queue) == 0


# Store queues per guild
music_queues = {}


def get_queue(guild_id):
    if guild_id not in music_queues:
        music_queues[guild_id] = MusicQueue()
    return music_queues[guild_id]


# ================================
# HELPER FUNCTIONS
# ================================

async def get_video_info(url: str):
    """Extract video information from URL"""
    loop = asyncio.get_event_loop()

    def extract():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            return {
                'url': info['url'],
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'webpage_url': info.get('webpage_url', url)
            }

    return await loop.run_in_executor(None, extract)


async def play_next(guild_id: int, interaction: discord.Interaction):
    """Play the next song in the queue"""
    queue = get_queue(guild_id)

    if queue.is_empty():
        queue.current = None
        return

    song = queue.get_next()
    queue.current = song

    def after_playing(error):
        if error:
            print(f"Error playing audio: {error}")

        # Play next song
        future = asyncio.run_coroutine_threadsafe(
            play_next(guild_id, interaction),
            bot.loop
        )
        try:
            future.result()
        except Exception as e:
            print(f"Error in after_playing: {e}")

    audio_source = discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS)
    queue.voice_client.play(audio_source, after=after_playing)


# ================================
# BOT EVENTS
# ================================

@bot.event
async def on_ready():
    print(f"✅ Bot is ready! Logged in as {bot.user}")
    print(f"📊 Connected to {len(bot.guilds)} server(s)")

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


# ================================
# SLASH COMMANDS
# ================================

@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    """Join the user's voice channel"""
    if not interaction.user.voice:
        await interaction.response.send_message("❌ You need to be in a voice channel!", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    queue = get_queue(interaction.guild.id)

    if queue.voice_client and queue.voice_client.is_connected():
        await queue.voice_client.move_to(channel)
        await interaction.response.send_message(f"🔊 Moved to **{channel.name}**")
    else:
        queue.voice_client = await channel.connect()
        await interaction.response.send_message(f"🔊 Joined **{channel.name}**")


@bot.tree.command(name="play", description="Play a song from YouTube")
@app_commands.describe(url="YouTube URL or search query")
async def play(interaction: discord.Interaction, url: str):
    """Play a song from YouTube"""
    await interaction.response.defer()

    # Check if user is in voice channel
    if not interaction.user.voice:
        await interaction.followup.send("❌ You need to be in a voice channel!")
        return

    queue = get_queue(interaction.guild.id)

    # Join voice channel if not connected
    if not queue.voice_client or not queue.voice_client.is_connected():
        channel = interaction.user.voice.channel
        queue.voice_client = await channel.connect()

    try:
        # Get video info
        song_info = await get_video_info(url)

        # Add to queue
        queue.add(song_info)

        # If nothing is playing, start playing
        if not queue.voice_client.is_playing() and not queue.current:
            await play_next(interaction.guild.id, interaction)
            await interaction.followup.send(f"🎵 Now playing: **{song_info['title']}**")
        else:
            await interaction.followup.send(f"➕ Added to queue: **{song_info['title']}**")

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")
        print(f"Error in play command: {e}")


@bot.tree.command(name="skip", description="Skip the current song")
async def skip(interaction: discord.Interaction):
    """Skip the current song"""
    queue = get_queue(interaction.guild.id)

    if not queue.voice_client or not queue.voice_client.is_playing():
        await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
        return

    queue.voice_client.stop()
    await interaction.response.send_message("⏭️ Skipped!")


@bot.tree.command(name="stop", description="Stop playing and clear the queue")
async def stop(interaction: discord.Interaction):
    """Stop playing and clear the queue"""
    queue = get_queue(interaction.guild.id)

    if not queue.voice_client:
        await interaction.response.send_message("❌ Bot is not connected to voice!", ephemeral=True)
        return

    queue.clear()
    queue.voice_client.stop()
    await interaction.response.send_message("⏹️ Stopped and cleared queue!")


@bot.tree.command(name="pause", description="Pause the current song")
async def pause(interaction: discord.Interaction):
    """Pause the current song"""
    queue = get_queue(interaction.guild.id)

    if queue.voice_client and queue.voice_client.is_playing():
        queue.voice_client.pause()
        await interaction.response.send_message("⏸️ Paused!")
    else:
        await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)


@bot.tree.command(name="resume", description="Resume the paused song")
async def resume(interaction: discord.Interaction):
    """Resume the paused song"""
    queue = get_queue(interaction.guild.id)

    if queue.voice_client and queue.voice_client.is_paused():
        queue.voice_client.resume()
        await interaction.response.send_message("▶️ Resumed!")
    else:
        await interaction.response.send_message("❌ Nothing is paused!", ephemeral=True)


@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    """Leave the voice channel"""
    queue = get_queue(interaction.guild.id)

    if queue.voice_client:
        queue.clear()
        await queue.voice_client.disconnect()
        await interaction.response.send_message("👋 Left the voice channel!")
    else:
        await interaction.response.send_message("❌ Bot is not in a voice channel!", ephemeral=True)


@bot.tree.command(name="queue", description="Show the current queue")
async def show_queue(interaction: discord.Interaction):
    """Display the current queue"""
    queue = get_queue(interaction.guild.id)

    if not queue.current and queue.is_empty():
        await interaction.response.send_message("📭 Queue is empty!", ephemeral=True)
        return

    embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.blue())

    if queue.current:
        embed.add_field(
            name="Now Playing",
            value=f"**{queue.current['title']}**",
            inline=False
        )

    if not queue.is_empty():
        queue_list = "\n".join([
            f"{i + 1}. {song['title']}"
            for i, song in enumerate(queue.queue[:10])
        ])
        embed.add_field(name="Up Next", value=queue_list, inline=False)

        if len(queue.queue) > 10:
            embed.add_field(name="", value=f"... and {len(queue.queue) - 10} more", inline=False)

    await interaction.response.send_message(embed=embed)


# ================================
# RUN BOT
# ================================

if __name__ == "__main__":
    print("🤖 Starting Discord Music Bot...")
    bot.run(BOT_TOKEN)