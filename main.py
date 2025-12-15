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

app = Client("YTShortsBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

# --- BUTTONS ---
def get_controls():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭ Agla Short (Next)", callback_data="next")],
        [InlineKeyboardButton("⏹ Band Karo (Stop)", callback_data="stop")]
    ])

# --- YOUTUBE DOWNLOADER ---
def get_random_short(chat_id):
    # Alag-alag topics search karega taaki bore na ho
    queries = ["trending shorts", "viral shorts", "funny shorts", "dance shorts", "tech shorts", "comedy shorts"]
    query = random.choice(queries)
    
    ydl_opts = {
        'format': 'best[ext=mp4]',  # Best MP4 Quality
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch5', # Top 5 results mein se choose karega
        'outtmpl': f'downloads/short_{chat_id}.%(ext)s',
        'geo_bypass': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"🔍 Searching YouTube for: {query}...")
            info = ydl.extract_info(query, download=False)
            
            if 'entries' in info:
                # Search results mein se random video pick karo
                video_entry = random.choice(info['entries'])
            else:
                video_entry = info

            video_url = video_entry['webpage_url']
            title = video_entry.get('title', 'Short Video')
            
            print(f"⬇️ Downloading: {title}")
            
            # File pehle se hai toh delete karo
            filename = f"downloads/short_{chat_id}.mp4"
            if os.path.exists(filename):
                os.remove(filename)

            ydl.download([video_url])
            
            return filename, title
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

# --- COMMANDS ---

@app.on_message(filters.command("play") & filters.group)
async def play_cmd(client, message):
    chat_id = message.chat.id
    msg = await message.reply_text("🔄 **YouTube Shorts dhoond raha hoon...**")

    # Background mein download karo
    filename, title = await asyncio.to_thread(get_random_short, chat_id)

    if not filename:
        await msg.edit_text("❌ Video nahi mili. Dobara /play dabao.")
        return

    await msg.edit_text(f"▶️ **Playing:** {title}", reply_markup=get_controls())

    try:
        # Video Stream Join karo
        await call.join_group_call(
            chat_id,
            MediaStream(video=filename, audio=filename)
        )
    except:
        # Agar pehle se joined hai, toh stream change karo
        try:
            await call.change_stream(
                chat_id,
                MediaStream(video=filename, audio=filename)
            )
        except Exception as e:
            await msg.edit_text(f"❌ Error: {e}")

@app.on_message(filters.command(["stop", "off"]) & filters.group)
async def stop_cmd(client, message):
    try:
        await call.leave_group_call(message.chat.id)
        await message.reply_text("✅ **Stream Stopped.**")
    except:
        await message.reply_text("❌ Bot call mein nahi hai.")

# --- BUTTON HANDLER (Next & Stop) ---
@app.on_callback_query()
async def handle_buttons(client, cb):
    data = cb.data
    chat_id = cb.message.chat.id

    if data == "stop":
        try:
            await call.leave_group_call(chat_id)
            await cb.message.delete() # Message delete kar do
        except:
            pass
        return

    if data == "next":
        # User ko batao ki load ho raha hai
        await cb.answer("🔄 Loading Next Short...", show_alert=False)
        
        filename, title = await asyncio.to_thread(get_random_short, chat_id)
        
        if filename:
            try:
                # Stream update karo
                await call.change_stream(
                    chat_id,
                    MediaStream(video=filename, audio=filename)
                )
                # Message update karo naye title ke saath
                await cb.message.edit_text(f"▶️ **Playing:** {title}", reply_markup=get_controls())
            except Exception as e:
                await cb.answer(f"Error: {e}", show_alert=True)
        else:
            await cb.answer("❌ Video nahi mili", show_alert=True)

if __name__ == "__main__":
    # Downloads folder banao agar nahi hai
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    print("🚀 YouTube Shorts Bot Started (No DB Mode)!")
    app.start()
    call.start()
    asyncio.get_event_loop().run_forever()
