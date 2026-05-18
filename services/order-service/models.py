from sqlalchemy import Column, Integer, String, Float, DateTime, func
from database import Base
from pydantic import BaseModel
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    product = Column(String)
    amount = Column(Float)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OrderCreate(BaseModel):
    user_id: int
    product: str
    amount: float

class OrderResponse(BaseModel):
    id: int
    user_id: int
    product: str
    amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
