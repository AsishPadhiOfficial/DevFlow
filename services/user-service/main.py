from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import engine, Base, get_db
from models import User, UserCreate, UserResponse
from publisher import publish_event

app = FastAPI(title="User Service")
Instrumentator().instrument(app).expose(app)

failure_counter = 0


@app.middleware("http")
async def simulate_failure_middleware(request: Request, call_next):
    global failure_counter
    if failure_counter > 0 and request.url.path not in ["/users/simulate-failure", "/health", "/metrics"]:
        failure_counter -= 1
        return JSONResponse(status_code=500, content={"detail": "Simulated failure"})
    return await call_next(request)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/users/simulate-failure")
async def simulate_failure():
    global failure_counter
    failure_counter = 5
    return {"message": "Next 5 requests will fail with 500"}


@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    await publish_event("user.created", {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    })

    return new_user


@app.get("/users", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}
