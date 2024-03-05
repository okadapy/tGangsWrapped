import uvicorn
from app.server import app as server
import asyncio

# async def start_bot():
#     print("Starting bot")
#     await dp.start_polling(bot)


async def start_server():
    print("starting server")
    uvicorn.run(server)


uvicorn.run(server)
