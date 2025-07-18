import asyncio
import logging
import sys
import wikipedia
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

API_TOKEN = "7953453670:AAEf4z0UwZPi9CCPGBpSQFh4fV92KAscWW0"
PEXELS_API_KEY = "rPEFYdGEJCEzlPtrnYtU0snhGDlPPl4zl6aqxQJ1opAFMqE1WhbldahD"

wikipedia.set_lang('uz')

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()



def search_pexels_images(query, count=2):
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": query,
        "per_page": count
    }
    response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return [photo["src"]["medium"] for photo in data.get("photos", [])]
    else:
        return []


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Salom, {message.from_user.first_name}! Habarchi Botiga xush kelibsiz!\n"
        "Qandaydir mavzu haqida ma’lumot olish uchun faqat mavzuni yozing.\n"
        "Masalan: <b>O'zbekiston</b>"
    )


@dp.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(
        f"Ushbu bot sizga Vikipediyadan ma’lumot va mavzuga oid Pexels rasmlarni yuboradi. Mavzuni kiriting va rasm bilan tanishing!"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        f" Salom {message.from_user.first_name}, iltimos qaysi muammoga yechim topmoqchi ekaningizni yozing")


@dp.message()
async def wikipedia_handler(message: types.Message):
    try:
        query = message.text
        summary = wikipedia.summary(query)
        await message.answer(f"<b>{query}</b> haqida ma’lumot:\n{summary}")

        images = search_pexels_images(query)
        if images:
            for img_url in images:
                await message.answer_photo(img_url)
        else:
            await message.answer("Afsus, bu mavzu bo‘yicha rasm topilmadi.")

    except wikipedia.exceptions.DisambiguationError as e:
        await message.answer(f"Bu mavzu bir nechta ma'noga ega:\n<b>{', '.join(e.options[:5])}</b>")
    except wikipedia.exceptions.PageError:
        await message.answer("Bunday mavzu topilmadi. Iltimos, boshqa so‘zni kiriting.")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi")


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
