from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db import Base

class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(String, unique=True, index=True, nullable=False)

    citizen_name = Column(String, nullable=True)

    description = Column(Text, nullable=False)

    department = Column(String, nullable=True)

    status = Column(String, default="OPEN", index=True)

    call_id = Column(String, index=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
