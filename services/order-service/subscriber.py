import os
import json
import asyncio
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")

async def start_subscriber():
    redis_client = redis.from_url(REDIS_URL)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("user.created")
    
    print("Order service subscribed to 'user.created' events")
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            event_data = json.loads(message["data"])
            print(f"Received event in Order Service: {event_data['event_type']} - Payload: {event_data['payload']}")
