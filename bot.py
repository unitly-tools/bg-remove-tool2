import os
import sys
import subprocess
import io
from io import BytesIO
from PIL import Image

# ---------- AUTO PACKAGE INSTALLER (Install rembg and its dependencies) ----------
# Ab aapko 'rembg' package ki zaroorat padegi.
required = ["pillow", "requests", "python-telegram-bot", "rembg"]
for pkg in required:
    try:
        # Check if package is installed before attempting to install
        __import__(pkg.split("==")[0])
    except ImportError:
        print(f"📦 Installing {pkg} ...")
        # Install the package
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", pkg])


# ---------- IMPORTS AND CONFIGURATION (Read from Environment Variables) ----------
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from rembg import remove # rembg library se remove function import kiya

# ⚠️ Ab sirf BOT_TOKEN ki zaroorat hai. REMOVE_BG_API_KEY ki zaroorat nahi hai.
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# REMOVE_BG_API_KEY variable ab unused hai aur hata diya gaya hai.


# ---------- BACKGROUND REMOVER FUNCTION (Local/Free Model) ----------
def remove_bg_local(image: Image.Image) -> BytesIO:
    """
    Removes background using the free local 'rembg' library (U-2-Net model).
    Returns processed image in BytesIO format.
    """
    print("🧠 Removing background using rembg...")
    
    # 1. Convert PIL Image to Bytes for rembg input
    input_buffer = BytesIO()
    image.save(input_buffer, format="PNG")
    input_buffer.seek(0)
    
    # 2. Process using rembg
    # Yeh automatically zaroori model download kar lega agar pehle se nahi hai.
    output_bytes = remove(input_buffer.read())
    
    # 3. Create BytesIO output
    result_buffer = BytesIO(output_bytes)
    result_buffer.seek(0)
    
    print("✅ Background removed successfully (using rembg)!")
    return result_buffer


# ---------- BOT COMMANDS (handle_image function updated) ----------
def start(update, context):
    update.message.reply_text(
        "👋 Hey! Send me a photo and I’ll remove its background for you instantly using a free model!"
    )


def help_command(update, context):
    update.message.reply_text("📸 Just send a photo — I’ll process it automatically.")


def handle_image(update, context):
    try:
        photo_sizes = update.message.photo
        if not photo_sizes:
            update.message.reply_text("🤔 Photo nahi mili. Please ek photo send karein.")
            return
            
        photo = photo_sizes[-1].get_file()
        file_bytes = BytesIO(photo.download_as_bytearray())
        # rembg ko input dene ke liye PNG format better hai
        image = Image.open(file_bytes).convert("RGB") # REMBG ke liye 'RGB' convert kiya

        update.message.reply_text("⏳ Removing background, please wait...")

        # Function call change kiya remove_bg_online se remove_bg_local mein
        result = remove_bg_local(image) 
        result.seek(0)

        update.message.reply_photo(photo=result, caption="✅ Done! Background removed successfully.", filename="removed_bg.png")
    except Exception as e:
        print(f"Error occurred: {e}")
        update.message.reply_text(f"❌ Operation fail ho gaya. Error: {str(e)}\n\n(Note: Pehli baar run hone par model download hone mein time lagta hai.)")


def handle_text(update, context):
    update.message.reply_text("💬 Please send an image, not text!")


# ---------- MAIN (No Change) ----------
def main():
    if not BOT_TOKEN:
        print("FATAL: BOT_TOKEN not found. Set it as an environment variable.")
        sys.exit(1)
        
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_text)) 

    print("🤖 Bot is running... Send /start in Telegram.")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
