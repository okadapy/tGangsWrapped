from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket
from fastapi.templating import Jinja2Templates
import asyncio
import random
import json
import time

app = FastAPI()
templates = Jinja2Templates("templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class Player:
    def __init__(self) -> None:
        self.canplace = False
        self.boost = False
        self.bomb = False
        self.lightning = 0
        self.armor = False

    def found_lightning(self):
        self.lightning = 5
        return {"type": "found", "buff": "lightning"}

    def found_bomb(self):
        self.bomb = True
        return {"type": "found", "buff": "bomb"}

    def found_boost(self):
        self.boost = True
        return {"type": "found", "buff": "boost"}


class Game:
    def __init__(self) -> None:
        self.grid = [
            [{"player": None, "armor": False} for x in range(20)] for y in range(20)
        ]

    def add_pixel(self, x, y, player):
        self.grid[y][x]["player"] = player

    def bomb(self, x, y, player):
        for n_y in range(y - 1, y + 1, 1):
            for n_x in range(x - 1, x + 1, 1):
                if self.grid[n_y][n_x] != player and not self.grid[n_y][n_x]["armor"]:
                    self.grid[n_y][n_x]["player"] = None

    def armor(self, x, y, player):
        for n_y in range(y - 1, y + 1, 1):
            for n_x in range(x - 1, x + 1, 1):
                if self.grid[n_y][n_x]["player"] == player and not self.grid[n_y][n_x]["armor"]:
                    self.grid[n_y][n_x]["armor"] = True

    def render(self, player):
        matrix = []
        for row in self.grid:
            node = []
            for item in row:
                if item["player"] == player:
                    new_item = {"player": 0, "armor": item["armor"]}
                    node.append(new_item)
                elif item["player"] == None:
                    new_item = {"player": None, "armor": item["armor"]}
                    node.append(new_item)
                else:
                    new_item = {"player": 1, "armor": item["armor"]}
                    node.append(new_item)

            matrix.append(node)

        return matrix


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[(WebSocket, Player)] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_matrix(self, to_player: WebSocket, matrix: list[dict]):
        await to_player.send_json({"type": "update", "data": matrix})

    async def broadcast_matrix(self, game: Game):
        for player in self.active_connections:
            matrix = game.render(players[player])
            await self.send_matrix(player, matrix)

    async def send_can_place(self, websocket: WebSocket, delay):
        await asyncio.sleep(delay)
        players[websocket].canplace = True
        await websocket.send_json({"type": "canclick"})


manager = ConnectionManager()
players: dict[WebSocket, Player] = {}
game = Game()
print(game.grid)
for row in game.grid:
    for item in row:
        print(item)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    await manager.connect(websocket)
    players[websocket] = Player()
    await manager.send_matrix(websocket, game.render(players[websocket]))
    await manager.send_can_place(websocket, 0)
    while True:
        try:
            data = await websocket.receive_json()
            if players[websocket].canplace:
                if data["type"] == "newpixel":
                    game.add_pixel(data["x"], data["y"], players[websocket])
                    if random.random() > 0.97:
                        await websocket.send_json(players[websocket].found_bomb())
                    elif random.random() > 0.85:
                        await websocket.send_json(players[websocket].found_boost())
                    elif random.random() > 0.80:
                        await websocket.send_json(players[websocket].found_lightning())
                    
                    players[websocket].canplace = False
                    if players[websocket].boost:
                        players[websocket].boost = False
                    elif players[websocket].lightning >= 1:
                        players[websocket].lightning -= 1
                    
                elif data["type"] == "bomb":
                    game.bomb(data["x"], data["y"], players[websocket])
                
                elif data["type"] == "armor":
                    game.armor(data["x"], data["y"], players[websocket])

                if players[websocket].boost:
                    await manager.send_can_place(websocket, 0)
                elif players[websocket].lightning >= 0:
                    asyncio.create_task(manager.send_can_place(websocket, 2))
                else:
                    asyncio.create_task(manager.send_can_place(websocket, 5))

                
                await manager.broadcast_matrix(game)

            
        except Exception as e:
            print(e)
            await manager.disconnect(websocket)
