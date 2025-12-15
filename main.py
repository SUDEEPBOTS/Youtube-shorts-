import os
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL

# --- CONFIG ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_STRING = os.getenv("SESSION_STRING") # <-- Ye zaroori hai ab

# --- CLIENTS SETUP ---
# 1. Bot Client (Commands ke liye)
bot = Client("Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 2. Assistant Client (Call Join karne ke liye)
user = Client("Userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# 3. PyTgCalls (User Client ko use karega)
call = PyTgCalls(user)

# --- BUTTONS ---
def get_controls():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭ Agla Short (Next)", callback_data="next")],
        [InlineKeyboardButton("⏹ Band Karo (Stop)", callback_data="stop")]
    ])

# --- YOUTUBE DOWNLOADER ---
def get_random_short(chat_id):
    queries = ["trending shorts", "viral shorts", "funny shorts", "dance shorts"]
    query = random.choice(queries)
    
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch5',
        'outtmpl': f'downloads/short_{chat_id}.%(ext)s',
        'geo_bypass': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"🔍 Searching: {query}...")
            info = ydl.extract_info(query, download=False)
            
            if 'entries' in info:
                video_entry = random.choice(info['entries'])
            else:
                video_entry = info

            video_url = video_entry['webpage_url']
            title = video_entry.get('title', 'Short Video')
            
            print(f"⬇️ Downloading: {title}")
            
            filename = f"downloads/short_{chat_id}.mp4"
            if os.path.exists(filename):
                os.remove(filename)

            ydl.download([video_url])
            return filename, title
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

# --- COMMANDS ---

@bot.on_message(filters.command("play") & filters.group)
async def play_cmd(client, message):
    chat_id = message.chat.id
    msg = await message.reply_text("🔄 **Assistant join kar raha hai...**")

    # Download karo
    filename, title = await asyncio.to_thread(get_random_short, chat_id)

    if not filename:
        await msg.edit_text("❌ Video nahi mili.")
        return

    await msg.edit_text(f"▶️ **Playing:** {title}", reply_markup=get_controls())

    try:
        # Userbot call join karega
        await call.join_group_call(
            chat_id,
            MediaStream(video=filename, audio=filename)
        )
    except:
        try:
            await call.change_stream(
                chat_id,
                MediaStream(video=filename, audio=filename)
            )
        except Exception as e:
            await msg.edit_text(f"❌ Error: {e}")

@bot.on_message(filters.command(["stop", "off"]) & filters.group)
async def stop_cmd(client, message):
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply_text("✅ **Assistant Left.**")
    except:
        await message.reply_text("❌ Assistant call mein nahi hai.")

# --- BUTTONS ---
@bot.on_callback_query()
async def handle_buttons(client, cb):
    data = cb.data
    chat_id = cb.message.chat.id

    if data == "stop":
        try:
            await call.leave_group_call(chat_id)
            await cb.message.delete()
        except:
            pass
        return

    if data == "next":
        await cb.answer("🔄 Loading Next...")
        filename, title = await asyncio.to_thread(get_random_short, chat_id)
        
        if filename:
            try:
                await call.change_stream(
                    chat_id,
                    MediaStream(video=filename, audio=filename)
                )
                await cb.message.edit_text(f"▶️ **Playing:** {title}", reply_markup=get_controls())
            except Exception as e:
                await cb.answer(f"Error: {e}", show_alert=True)

# --- STARTUP ---
async def start_bot():
    print("🚀 Starting Bot & Assistant...")
    await bot.start()
    await user.start()
    await call.start()
    print("✅ System Online!")
    await asyncio.get_event_loop().create_future() # Keep running

if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    asyncio.run(start_bot())
    
