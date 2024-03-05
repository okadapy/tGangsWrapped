from app.bot import dp, bot

import asyncio

async def start_bot():
    print("Starting bot")
    await dp.start_polling(bot)

