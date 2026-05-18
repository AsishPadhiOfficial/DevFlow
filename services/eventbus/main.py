import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import redis.asyncio as redis

app = FastAPI(title="EventBus Service")
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)

manager = ConnectionManager()

async def redis_listener():
    redis_client = redis.from_url(REDIS_URL)
    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("*")
    
    print("EventBus subscribed to ALL Redis channels")
    
    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            channel = message["channel"].decode('utf-8')
            event_data = message["data"].decode('utf-8')
            
            # Broadcast the raw JSON data to all websocket clients
            await manager.broadcast(event_data)

@app.on_event("startup")
async def startup_event():
    app.state.redis_listener_task = asyncio.create_task(redis_listener())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect messages from client, but keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
