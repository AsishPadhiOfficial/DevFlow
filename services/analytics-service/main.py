import asyncio
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta

from database import engine, Base, get_db
from models import EventLog
from subscriber import start_subscriber

app = FastAPI(title="Analytics Service")
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start the subscriber as a background task and keep a strong reference
    app.state.subscriber_task = asyncio.create_task(start_subscriber())

@app.get("/analytics/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    # Total users
    users_result = await db.execute(select(func.count(EventLog.id)).where(EventLog.event_type == "user.created"))
    total_users = users_result.scalar() or 0

    # Total orders
    orders_result = await db.execute(select(func.count(EventLog.id)).where(EventLog.event_type == "order.created"))
    total_orders = orders_result.scalar() or 0

    # Events per minute (last 60 minutes)
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    
    events_query = select(
        func.date_trunc('minute', EventLog.received_at).label('minute'),
        func.count(EventLog.id).label('count')
    ).where(
        EventLog.received_at >= one_hour_ago
    ).group_by(
        'minute'
    ).order_by(
        'minute'
    )
    
    events_result = await db.execute(events_query)
    events_per_minute = [{"time": row.minute.isoformat(), "count": row.count} for row in events_result]

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "events_per_minute": events_per_minute
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics-service"}
