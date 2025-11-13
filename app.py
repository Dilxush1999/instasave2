import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot token'ingizni bu yerga qo'ying
BOT_TOKEN = '7847208260:AAFszXaZjbMRA6N6Vsr9t9XBZywLpMQBLkU'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start buyrug'i handleri: Link so'raydi """
    await update.message.reply_text(
        "Salom! Instagram linkini yuboring. Men uni yuklab beraman! 📱"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Oddiy xabar handleri: Instagram linkini qayta ishlaydi """
    user_message = update.message.text
    if not user_message:
        return  # Agar matn bo'lmasa, e'tiborsiz qoldir

    # Instagram linkini tekshirish (instagram.com borligini qidirish)
    if 'instagram.com' in user_message:
        # www. ni kk ga almashtirish
        modified_link = re.sub(r'https://www\.instagram\.com/', 'https://kkinstagram.com/', user_message)
        
        # O'zgartirilgan linkni video sifatida yuborish
        await update.message.reply_video(
            video=modified_link,
            caption="@Instayoutubesave_bot 🎥"
        )
    else:
        await update.message.reply_text(
            "Iltimos, faqat Instagram linkini yuboring. Misol: https://www.instagram.com/reel/..."
        )

def main():
    """ Botni ishga tushirish """
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Botni ishga tushirish
    print("Bot ishga tushdi! /start buyrug'ini sinab ko'ring.")
    application.run_polling()

if __name__ == '__main__':
    main()
