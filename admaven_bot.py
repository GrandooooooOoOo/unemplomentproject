import os
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import requests
from urllib.parse import quote

# Get tokens from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADM_TOKEN = os.getenv("ADM_TOKEN")

ADM_URL = "https://publishers.ad-maven.com/api/public/content_locker "

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    if user_input.startswith(('http://', 'https://')):
        await update.message.reply_text("🔗 Locking your link with AdMaven...")

        title = "Locked Content"
        encoded_url = quote(user_input)

        headers = {
            "Authorization": f"Bearer {ADM_TOKEN}"
        }

        payload = {
            "title": title,
            "url": encoded_url,
        }

        try:
            response = requests.post(ADM_URL, headers=headers, data=payload)
            data = response.json()

            if data.get('type') == 'created':
                short_link = data['message']['desturl']
                await update.message.reply_text(f"✅ Monetized Link:\n\n{short_link}")
            else:
                error_msg = data.get('message', 'Unknown error')
                await update.message.reply_text(f"❌ Failed: {error_msg}")

        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {str(e)}")
    else:
        await update.message.reply_text("⚠️ Please send a valid link.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    app.add_handler(handler)
    app.run_polling()
