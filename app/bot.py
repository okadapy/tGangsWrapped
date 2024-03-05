from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.filters import CommandStart
from config import BOT_TOKEN, WEB_APP_URL

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start(m: Message):
    await m.answer(
        "Представим, что тут есть какое то приветствие",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Начать игру", web_app=WebAppInfo(url=WEB_APP_URL)
                    )
                ]
            ]
        ),
    )
