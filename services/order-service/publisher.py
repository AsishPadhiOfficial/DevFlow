import os
import json
import redis.asyncio as redis
from datetime import datetime

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")
redis_client = redis.from_url(REDIS_URL)


async def publish_event(event_type: str, payload: dict):
    event = {
        "event_type": event_type,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat()
    }
    await redis_client.publish(event_type, json.dumps(event))
    print(f"Published event: {event_type}")
