import os
import json
import redis.asyncio as redis
from database import async_session
from models import Notification

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")

async def process_event(channel: str, event_data: dict):
    payload = event_data.get("payload", {})
    
    if channel == b"user.created":
        email = payload.get("email", "unknown")
        message = f"Welcome {payload.get('name', 'User')}! Your account has been created."
        notif_type = "WELCOME"
    elif channel == b"order.created":
        email = f"user_{payload.get('user_id')}@example.com" # Mocking email retrieval
        message = f"Order confirmation for {payload.get('product')} (Amount: {payload.get('amount')})."
        notif_type = "ORDER_CONFIRMATION"
    else:
        return

    async with async_session() as db:
        new_notification = Notification(
            type=notif_type,
            recipient_email=email,
            message=message,
            event_source=event_data.get("event_type", "unknown")
        )
        db.add(new_notification)
        await db.commit()
        print(f"Sent notification: {message} to {email}")

async def start_subscriber():
    redis_client = redis.from_url(REDIS_URL)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("user.created", "order.created")
    
    print("Notification service subscribed to 'user.created' and 'order.created' events")
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            channel = message["channel"]
            event_data = json.loads(message["data"])
            await process_event(channel, event_data)
