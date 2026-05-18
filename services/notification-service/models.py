from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base
from pydantic import BaseModel
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    recipient_email = Column(String)
    message = Column(String)
    event_source = Column(String)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationResponse(BaseModel):
    id: int
    type: str
    recipient_email: str
    message: str
    event_source: str
    sent_at: datetime

    class Config:
        from_attributes = True
