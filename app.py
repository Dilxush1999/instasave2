import re
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging: Render logs uchun
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token env'dan (Render uchun)
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN topilmadi! Render env'ga qo'shing.")
    raise ValueError("BOT_TOKEN kerak!")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Global error handler: Xatoni log'la, botni to'xtatma """
    logger.error(f"Xato: {context.error}", exc_info=context.error)
    if update and update.message:
        await update.message.reply_text("❌ Kechirasiz, xato yuz berdi. /start qayta yuboring.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start: Link so'raydi """
    try:
        await update.message.reply_text(
            "Salom! Instagram video yoki post linkini yuboring. Men uni yuklab beraman! 📱"
        )
    except Exception as e:
        logger.error(f"Start xatosi: {e}")
        await update.message.reply_text("❌ Start'da xato. Qayta urinib ko'ring.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Link handler: Robust """
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
        
        # Video yuborish
        await update.message.reply_video(
            video=modified_link,
            caption="Mana sizning videongiz! 🎥"
        )
    except Exception as e:
        logger.error(f"Message handler xatosi: {e}")
        await update.message.reply_text("❌ Videoni yuborishda xato. Linkni tekshiring va qayta yuboring.")

def main():
    """ Bot ishga tushirish: Robust rejim """
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)  # Parallel foydalanuvchilar
        .build()
    )

    # Handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Global error
    application.add_error_handler(error_handler)

    logger.info("🤖 Bot ishga tushdi! Render rejimida.")
    # Polling: Eski xabarlarni tashla, timeout
    application.run_polling(
        drop_pending_updates=True,
        poll_interval=1.0,
        timeout=10,
        bootstrap_retries=-1  # Cheksiz retry
    )

if __name__ == '__main__':
    main()
