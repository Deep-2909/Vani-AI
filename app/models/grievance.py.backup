from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.db import Base
import enum

# Define enums for database
class ComplaintStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"
    PENDING_INFO = "PENDING_INFO"

class Priority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    citizen_name = Column(String(255), nullable=True)
    contact = Column(String(15), nullable=True, index=True)  # Mobile number
    
    # Complaint Details
    description = Column(Text, nullable=False)
    location = Column(String(500), nullable=True)  # Specific area/address
    
    # Classification
    department = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)  # NEW: Specific category
    priority = Column(String(20), nullable=True, index=True)  # NEW: Priority level
    
    # Status Tracking
    status = Column(String(50), default="OPEN", index=True)
    
    # Technical Details
    call_id = Column(String(100), index=True, nullable=True)  # Retell call ID
    
    # Escalation
    escalated = Column(Integer, default=0)  # Number of times escalated
    escalation_reason = Column(Text, nullable=True)  # Latest escalation reason
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional tracking
    assigned_to = Column(String(255), nullable=True)  # Department officer assigned
    remarks = Column(Text, nullable=True)  # Internal remarks


class StatusCheck(Base):
    """Track status check requests"""
    __tablename__ = "status_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), index=True, nullable=False)
    phone_number = Column(String(15), nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    call_id = Column(String(100), nullable=True)


class Escalation(Base):
    """Track complaint escalations"""
    __tablename__ = "escalations"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), index=True, nullable=False)
    reason = Column(Text, nullable=False)
    escalated_by = Column(String(15), nullable=True)  # Phone number
    escalated_at = Column(DateTime(timezone=True), server_default=func.now())
    escalated_to = Column(String(255), nullable=True)  # Higher authority
    call_id = Column(String(100), nullable=True)


class Feedback(Base):
    """Store citizen feedback"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), index=True, nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5
    feedback_text = Column(Text, nullable=False)
    phone_number = Column(String(15), nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    call_id = Column(String(100), nullable=True)


class Emergency(Base):
    """Track emergency calls"""
    __tablename__ = "emergencies"
    
    id = Column(Integer, primary_key=True, index=True)
    emergency_type = Column(String(50), nullable=False, index=True)
    location = Column(String(500), nullable=False)
    phone_number = Column(String(15), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    call_id = Column(String(100), nullable=True)
