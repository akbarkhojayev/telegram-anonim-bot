import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from collections import defaultdict

BOT_TOKEN = "7701647980:AAHdiU2wIA8wG9TYznd8TFSgi-iNC-SPTq4"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

active_chats = {}

@dp.message(CommandStart(deep_link=True))
async def start_with_link(message: Message, command: CommandStart):
    user_id = message.from_user.id
    args = command.args

    if args.startswith("chat_"):
        target_id = int(args.split("_")[1])

        if user_id == target_id:
            return await message.answer("❌ Вы не можете отправить анонимное сообщение самому себе.")

        active_chats[user_id] = target_id
        active_chats[target_id] = user_id

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Завершить чат", callback_data="end_chat")]
            ]
        )

        await bot.send_message(user_id, "Вы теперь в анонимном чате. Напишите сообщение!", reply_markup=keyboard)
        await bot.send_message(target_id, "Кто-то пишет вам анонимно!", reply_markup=keyboard)
    else:
        link = f"https://t.me/{(await bot.get_me()).username}?start=chat_{user_id}"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📤 Поделиться", switch_inline_query=link)]
            ]
        )

        await message.answer(
            f"📨 Хотите получать анонимные сообщения от друзей?\n\n"
            f"🔗 Ваша ссылка:\n{link}\n\n"
            f"☝️Запости эту ссылку в Telegram-канале, или своём профиле",
            reply_markup=keyboard
        )

@dp.message(Command("start"))
async def start_without_args(message: Message):
    user_id = message.from_user.id
    link = f"https://t.me/{(await bot.get_me()).username}?start=chat_{user_id}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Поделиться", switch_inline_query=link)]
        ]
    )

    await message.answer(
        f"📨 Хотите получать анонимные сообщения от друзей?\n\n"
        f"🔗 Ваша ссылка:\n{link}\n\n"
        f"☝️Запости эту ссылку в Telegram-канале, или своём профиле",
        reply_markup=keyboard
    )

@dp.message(F.text & ~F.via_bot)
async def handle_message(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        target_id = active_chats[user_id]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="↩️ Ответить", callback_data=f"reply_{user_id}")]
            ]
        )

        await bot.send_message(chat_id=target_id, text=f"📨 Получено сообщение!\n\n  {message.text}", reply_markup=keyboard)
        await message.answer("✅ Сообщение отправлено!")
    else:
        await message.answer("❌ Вы сейчас ни с кем не в чате.")

@dp.callback_query(F.data.startswith("reply_"))
async def reply_callback(query: CallbackQuery):
    from_user = query.from_user.id
    target_id = int(query.data.split("_")[1])

    active_chats[from_user] = target_id
    active_chats[target_id] = from_user

    await bot.send_message(chat_id=from_user, text="✍️ Напишите ваш ответ:")
    await query.answer()

@dp.callback_query(F.data == "end_chat")
async def end_chat(query: CallbackQuery):
    user_id = query.from_user.id

    if user_id in active_chats:
        target_id = active_chats[user_id]
        del active_chats[user_id]
        del active_chats[target_id]

        await bot.send_message(chat_id=target_id, text="❌ Анонимный чат завершён.")
        await bot.send_message(chat_id=user_id, text="❌ Чат завершён.")
    else:
        await query.message.answer("❌ Вы ни с кем не в чате.")

    await query.answer()

async def main():
    print("Bot ishga tushdi !!!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
