from prometheus_fastapi_instrumentator import Instrumentator
import asyncio
import httpx
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import engine, Base, get_db
from models import Order, OrderCreate, OrderResponse
from publisher import publish_event
from subscriber import start_subscriber
from circuit_breaker import CircuitBreaker

app = FastAPI(title="Order Service")
Instrumentator().instrument(app).expose(app)

user_service_cb = CircuitBreaker(
    "user-service", expected_exception=httpx.HTTPError)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start the subscriber as a background task
    app.state.subscriber_task = asyncio.create_task(start_subscriber())


@app.get("/orders/circuit-breakers")
async def get_circuit_breakers():
    return {
        "service": "order-service",
        "circuit_breakers": [
            user_service_cb.get_state()
        ]
    }


@app.post("/orders")
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    # Validate user via user-service
    async def fetch_user():
        async with httpx.AsyncClient() as client:
            res = await client.get(f"http://user-service:8001/users/{order.user_id}", timeout=2.0)
            res.raise_for_status()
            return res.json()

    user_validation_failed = False
    try:
        await user_service_cb.call(fetch_user)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=400, detail="User not found")
        user_validation_failed = True
    except Exception:
        user_validation_failed = True

    new_order = Order(
        user_id=order.user_id,
        product=order.product,
        amount=order.amount
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    # Publish event
    await publish_event("order.created", {
        "id": new_order.id,
        "user_id": new_order.user_id,
        "product": new_order.product,
        "amount": new_order.amount,
        "status": new_order.status
    })

    if user_validation_failed:
        return JSONResponse(status_code=202, content={"detail": "User validation unavailable, order queued"})

    return new_order


@app.get("/orders", response_model=List[OrderResponse])
async def list_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    return orders


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}
