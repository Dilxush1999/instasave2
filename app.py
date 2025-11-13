import re
import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token env'dan
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN kerak!")

# Flask app (Render uchun)
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

# Webhook endpoint (Render uchun /webhook)
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return 'OK'

@app.route('/')
def index():
    return "Bot ishga tushdi! Webhook rejimida."

def main():
    # Webhook o'rnatish (bir marta ishga tushganda)
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://your-service.onrender.com/webhook')  # Render URL'ni env'ga qo'shing
    application.bot.set_webhook(WEBHOOK_URL)
    logger.info(f"🤖 Webhook o'rnatildi: {WEBHOOK_URL}")
    logger.info("Bot tayyor! Render Web Service sifatida ishlaydi.")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

if __name__ == '__main__':
    main()
