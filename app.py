import re
import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token va URL env'dan
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # Placeholder o'chirildi – majburiy env
if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN va WEBHOOK_URL env'ga kerak!")

# Flask app
app = Flask(__name__)

# Telegram app
application = (
    Application.builder()
    .token(BOT_TOKEN)
    .concurrent_updates(True)
    .build()
)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Xato: {context.error}", exc_info=context.error)
    if update and update.message:
        await update.message.reply_text("❌ Xato yuz berdi. /start qayta yuboring.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Salom! Instagram video yoki post linkini yuboring. Men uni yuklab beraman! 📱"
        )
    except Exception as e:
        logger.error(f"Start xatosi: {e}")
        await update.message.reply_text("❌ Start'da xato.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        if not user_message:
            return
        if 'instagram.com' not in user_message:
            await update.message.reply_text(
                "Iltimos, faqat Instagram linkini yuboring. Misol: https://www.instagram.com/reel/..."
            )
            return
        # www. ni kk ga almashtirish
        modified_link = re.sub(r'https://www\.instagram\.com/', 'https://kkinstagram.com/', user_message)
        await update.message.reply_video(
            video=modified_link,
            caption="Mana sizning videongiz! 🎥"
        )
    except Exception as e:
        logger.error(f"Message xatosi: {e}")
        await update.message.reply_text("❌ Videoni yuborishda xato. Qayta urinib ko'ring.")

# Handlerlar
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_error_handler(error_handler)

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), application.bot)
        asyncio.create_task(application.process_update(update))  # Async process
        return 'OK'
    except Exception as e:
        logger.error(f"Webhook xatosi: {e}")
        return 'Error', 500

@app.route('/')
def index():
    return "Bot ishga tushdi! Webhook rejimida."

async def main():
    """ Async main: Webhook o'rnatish """
    try:
        # Webhook o'rnatish (await bilan)
        await application.bot.set_webhook(WEBHOOK_URL)
        webhook_info = await application.bot.get_webhook_info()
        if webhook_info.url == WEBHOOK_URL:
            logger.info(f"✅ Webhook muvaffaqiyatli o'rnatildi: {WEBHOOK_URL}")
        else:
            logger.error(f"❌ Webhook o'rnatilmadi! Joriy: {webhook_info.url}")
    except TelegramError as e:
        logger.error(f"Webhook o'rnatish xatosi: {e}")
        raise
    logger.info("🤖 Bot tayyor! Render Web Service sifatida ishlaydi.")
    # Flask server'ni boshlash (sinxron)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    asyncio.run(main())
