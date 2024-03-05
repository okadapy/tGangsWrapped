import uvicorn
from app.server import app as server
import asyncio

async def start_server():
    print("starting server")
    uvicorn.run(server, port=90, host="0.0.0.0", reload=True)


uvicorn.run(server)
