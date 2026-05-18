from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from database import Base


class EventLog(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    payload = Column(JSON)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
