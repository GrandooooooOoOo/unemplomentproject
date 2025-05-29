# admaven_bot.py

import os
import logging
import requests  # For making API calls to AdMaven
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === CONFIGURATION ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADM_TOKEN = os.getenv("ADM_TOKEN")

ADM_API_URL = "https://publishers.ad-maven.com/api/public/content_locker "

# === LOGGING SETUP ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === MESSAGE HANDLER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    if user_input.startswith(('http://', 'https://')):
        await update.message.reply_text("🔗 Locking your link with AdMaven...")

        title = "Locked Content"
        encoded_url = user_input  # Requests handles the encoding automatically

        headers = {
            "Authorization": f"Bearer {ADM_TOKEN}"
        }

        payload = {
            "title": title,
            "url": encoded_url,
        }

        try:
            response = requests.post(ADM_API_URL, headers=headers, data=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()

            if data.get('type') == 'created':
                short_link = data['message']['desturl']
                await update.message.reply_text(f"✅ Your monetized link is ready:\n\n{short_link}")
            else:
                error_msg = data.get('message', 'Unknown error occurred.')
                await update.message.reply_text(f"❌ Failed to create link:\n{error_msg}")

        except requests.exceptions.RequestException as e:
            await update.message.reply_text(f"⚠️ Network error contacting AdMaven API:\n{str(e)}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Unexpected error:\n{str(e)}")
    else:
        await update.message.reply_text("⚠️ Please send a valid link (starting with http:// or https://).")

# === START BOT ===
if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN or not ADM_TOKEN:
        raise ValueError("Missing environment variables: TELEGRAM_BOT_TOKEN or ADM_TOKEN")

    print("🚀 Bot is running...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    app.add_handler(handler)
    app.run_polling()
