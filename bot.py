import os
import sys
import subprocess
import io
from io import BytesIO
from PIL import Image

# ---------- AUTO PACKAGE INSTALLER (No change) ----------
required = ["pillow", "requests", "python-telegram-bot", "rembg", "onnxruntime"]
for pkg in required:
    try:
        __import__(pkg.split("==")[0])
    except ImportError:
        print(f"📦 Installing {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", pkg])


# ---------- IMPORTS AND CONFIGURATION (Application class use kiya) ----------
from telegram.ext import Application, CommandHandler, MessageHandler, filters 
from rembg import remove 

BOT_TOKEN = os.environ.get("BOT_TOKEN")


# ---------- BACKGROUND REMOVER FUNCTION (No Change) ----------
def remove_bg_local(image: Image.Image) -> BytesIO:
    print("🧠 Removing background using rembg...")
    input_buffer = BytesIO()
    image.save(input_buffer, format="PNG")
    input_buffer.seek(0)
    
    output_bytes = remove(input_buffer.read())
    
    result_buffer = BytesIO(output_bytes)
    result_buffer.seek(0)
    
    print("✅ Background removed successfully (using rembg)!")
    return result_buffer


# ---------- BOT COMMANDS (No Change) ----------
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
        image = Image.open(file_bytes).convert("RGB") 

        update.message.reply_text("⏳ Removing background, please wait...")

        result = remove_bg_local(image) 
        result.seek(0)

        update.message.reply_photo(photo=result, caption="✅ Done! Background removed successfully.", filename="removed_bg.png")
    except Exception as e:
        print(f"Error occurred: {e}")
        update.message.reply_text(f"❌ Operation fail ho gaya. Error: {str(e)}\n\n(Note: Pehli baar run hone par model download hone mein time lagta hai.)")


def handle_text(update, context):
    update.message.reply_text("💬 Please send an image, not text!")


# ---------- MAIN (Updated for Application) ----------
def main():
    if not BOT_TOKEN:
        print("FATAL: BOT_TOKEN not found. Set it as an environment variable.")
        sys.exit(1)
        
    # Updater is replaced by Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # dp is now the application instance
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image)) 
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text)) 

    print("🤖 Bot is running... Send /start in Telegram.")
    
    # start_polling is replaced by run_polling
    application.run_polling() 


if __name__ == "__main__":
    main()
