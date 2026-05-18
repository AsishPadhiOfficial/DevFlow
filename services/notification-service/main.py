import asyncio
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import engine, Base, get_db
from models import Notification, NotificationResponse
from subscriber import start_subscriber

app = FastAPI(title="Notification Service")
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start the subscriber as a background task
    asyncio.create_task(start_subscriber())

@app.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification))
    notifications = result.scalars().all()
    return notifications

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}
