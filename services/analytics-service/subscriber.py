import os
import json
import redis.asyncio as redis
from database import async_session
from models import EventLog

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")


async def process_event(event_data: dict):
    async with async_session() as db:
        new_event = EventLog(
            event_type=event_data.get("event_type", "unknown"),
            payload=event_data.get("payload", {})
        )
        db.add(new_event)
        await db.commit()


async def start_subscriber():
    redis_client = redis.from_url(REDIS_URL)
    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("*")  # Subscribe to all events

    print("Analytics service subscribed to ALL events")

    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            event_data = json.loads(message["data"])
            await process_event(event_data)
