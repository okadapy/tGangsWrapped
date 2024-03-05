import uvicorn
from app.server import app as server
import asyncio

uvicorn.run(server, port=8000, host="0.0.0.0")
