from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

active_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if args and args[0].startswith("chat_"):
        target_id = args[0].split("_")[1]

        if target_id.isdigit():
            target_id = int(target_id)

            if user_id == target_id:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ Siz o'zingizga anonim ravishda xabar yuborolmaysiz."
                )
                return

            active_chats[user_id] = target_id
            active_chats[target_id] = user_id

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Suhbatni tugatish", callback_data="end_chat")]
            ])

            await context.bot.send_message(chat_id=user_id, text="Siz endi anonim suhbatdasiz. Xabar yozing!", reply_markup=keyboard)
            await context.bot.send_message(chat_id=target_id, text="Kimdir sizga anonim ravishda yozmoqda!", reply_markup=keyboard)
            return

    link = f"https://t.me/{context.bot.username}?start=chat_{user_id}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 Ulashish",
                switch_inline_query=f"{link}"
            )
        ]
    ])

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "📨Do'stlaringizdan anonim xabarlar olishni xohlaysizmi?\n\n"
            f"🔗Mana sizning shaxsiy havolangiz:\n{link}\n\n"
            "☝️Ushbu havolani Telegram kanalingizga yoki profilingizga joylang"
        ),
        reply_markup=keyboard
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        target_id = active_chats[user_id]

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ Javob qaytarish", callback_data=f"reply_{user_id}")]
        ])

        await context.bot.send_message(chat_id=target_id, text=update.message.text, reply_markup=keyboard)
        await context.bot.send_message(chat_id=user_id, text="✅ Xabar yuborildi!")
    else:
        await update.message.reply_text("Siz hozirda hech kim bilan suhbatda emassiz.")

async def reply_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data.startswith("reply_"):
        target_id = int(query.data.split("_")[1])

        await query.message.reply_text("✍️ Javobingizni yozing:")

        active_chats[user_id] = target_id
        await query.answer()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in active_chats:
        target_id = active_chats[user_id]

        del active_chats[user_id]
        del active_chats[target_id]

        await context.bot.send_message(chat_id=target_id, text="❌ Anonim suhbat tugatildi.")
        await query.message.reply_text("❌ Suhbat tugatildi.")
    else:
        await query.message.reply_text("Siz hozirda hech kim bilan suhbatda emassiz.")

    await query.answer()

def main():
    TOKEN = "" #Telegram bot token
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(CallbackQueryHandler(reply_button_handler, pattern="^reply_"))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="end_chat"))

    print("Bot ishga tushdi...")
    application.run_polling()

if __name__ == "__main__":
    main()
