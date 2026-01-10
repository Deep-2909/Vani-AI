from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func
from app.db import Base

# ===================================================================
# EXISTING TABLES (Enhanced)
# ===================================================================

class Grievance(Base):
    """Main grievances table"""
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    citizen_name = Column(String(255), nullable=True)
    contact = Column(String(15), nullable=True, index=True)
    
    # Complaint Details
    description = Column(Text, nullable=False)
    location = Column(String(500), nullable=True)
    area = Column(String(200), nullable=True, index=True)  # Normalized area name
    
    # Classification
    department = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    priority = Column(String(20), nullable=True, index=True)
    
    # Status Tracking
    status = Column(String(50), default="OPEN", index=True)
    
    # Technical Details
    call_id = Column(String(100), index=True, nullable=True)
    
    # Escalation
    escalated = Column(Integer, default=0)
    escalation_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional tracking
    assigned_to = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Language
    language = Column(String(20), default="english")  # hindi, punjabi, english


# ===================================================================
# NEW TABLE: RESOLVED COMPLAINTS
# ===================================================================

class ResolvedComplaint(Base):
    """Archive of resolved complaints"""
    __tablename__ = "complaints_resolved"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Original complaint data (copied from grievances)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    citizen_name = Column(String(255))
    contact = Column(String(15), index=True)
    description = Column(Text)
    location = Column(String(500))
    area = Column(String(200), index=True)
    department = Column(String(100), index=True)
    category = Column(String(100), index=True)
    priority = Column(String(20))
    call_id = Column(String(100))
    
    # Resolution details
    resolved_by = Column(String(255), nullable=False)  # Manager/officer name
    resolution_notes = Column(Text)
    resolution_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Original timestamps
    complaint_created_at = Column(DateTime(timezone=True))
    complaint_resolved_at = Column(DateTime(timezone=True))
    
    # Metrics
    resolution_time_hours = Column(Float)  # Time taken to resolve
    
    # Citizen satisfaction
    citizen_rating = Column(Integer, nullable=True)  # From feedback
    citizen_feedback = Column(Text, nullable=True)
    
    # Transfer metadata
    transferred_at = Column(DateTime(timezone=True), server_default=func.now())
    transferred_by = Column(String(255))  # Who moved it to resolved


# ===================================================================
# NEW TABLE: AREA HOTSPOTS
# ===================================================================

class AreaHotspot(Base):
    """Track complaint density by area"""
    __tablename__ = "area_hotspots"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Area identification
    area_name = Column(String(200), unique=True, index=True, nullable=False)
    normalized_name = Column(String(200), index=True)  # Cleaned version
    
    # Complaint counts
    total_complaints = Column(Integer, default=0)
    open_complaints = Column(Integer, default=0)
    resolved_complaints = Column(Integer, default=0)
    
    # By category
    water_complaints = Column(Integer, default=0)
    road_complaints = Column(Integer, default=0)
    electricity_complaints = Column(Integer, default=0)
    pollution_complaints = Column(Integer, default=0)
    other_complaints = Column(Integer, default=0)
    
    # Priority breakdown
    critical_complaints = Column(Integer, default=0)
    high_complaints = Column(Integer, default=0)
    medium_complaints = Column(Integer, default=0)
    low_complaints = Column(Integer, default=0)
    
    # Status flags
    is_hotspot = Column(Boolean, default=False, index=True)
    hotspot_level = Column(String(20), nullable=True)  # WARNING, CRITICAL, SEVERE
    flagged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Thresholds (configurable per area)
    warning_threshold = Column(Integer, default=10)
    critical_threshold = Column(Integer, default=25)
    severe_threshold = Column(Integer, default=50)
    
    # Timestamps
    first_complaint_at = Column(DateTime(timezone=True))
    last_complaint_at = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Alert status
    alert_sent = Column(Boolean, default=False)
    alert_sent_at = Column(DateTime(timezone=True), nullable=True)


# ===================================================================
# NEW TABLE: OUTBOUND CALLS LOG
# ===================================================================

class OutboundCall(Base):
    """Track government-initiated calls"""
    __tablename__ = "outbound_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Call details
    call_id = Column(String(100), unique=True, index=True)
    phone_number = Column(String(15), nullable=False, index=True)
    
    # Purpose
    call_type = Column(String(50), nullable=False, index=True)
    # Types: scheme_notification, alert, follow_up, survey, announcement
    
    # Content
    message_template = Column(String(100))  # Which template was used
    message_content = Column(Text)
    
    # Related data
    related_ticket_id = Column(String(50), nullable=True, index=True)
    scheme_name = Column(String(255), nullable=True)
    alert_type = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(50), default="PENDING")
    # PENDING, INITIATED, CONNECTED, COMPLETED, FAILED, NO_ANSWER
    
    # Timestamps
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    initiated_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Call metrics
    duration_seconds = Column(Integer, nullable=True)
    answered = Column(Boolean, default=False)
    
    # Response tracking
    user_response = Column(Text, nullable=True)
    action_taken = Column(String(100), nullable=True)
    
    # Initiated by
    initiated_by = Column(String(255))  # System/Manager name
    
    # Language
    language = Column(String(20), default="hindi")


# ===================================================================
# NEW TABLE: GOVERNMENT SCHEMES
# ===================================================================

class GovernmentScheme(Base):
    """Store government schemes for outbound notifications"""
    __tablename__ = "government_schemes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Scheme details
    scheme_code = Column(String(50), unique=True, index=True)
    scheme_name = Column(String(255), nullable=False)
    department = Column(String(100), index=True)
    
    # Description
    short_description = Column(Text)
    full_description = Column(Text)
    
    # Eligibility
    eligibility_criteria = Column(Text)
    target_areas = Column(Text)  # JSON list of areas
    target_categories = Column(Text)  # JSON list of categories
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Outbound campaign
    send_notifications = Column(Boolean, default=False)
    notification_message = Column(Text)
    
    # Links
    application_url = Column(String(500), nullable=True)
    helpline_number = Column(String(15), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ===================================================================
# EXISTING TABLES (Unchanged)
# ===================================================================

class StatusCheck(Base):
    __tablename__ = "status_checks"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), index=True, nullable=False)
    phone_number = Column(String(15), nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    call_id = Column(String(100), nullable=True)


class Escalation(Base):
    __tablename__ = "escalations"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), index=True, nullable=False)
    reason = Column(Text, nullable=False)
    escalated_by = Column(String(15), nullable=True)
    escalated_at = Column(DateTime(timezone=True), server_default=func.now())
    escalated_to = Column(String(255), nullable=True)
    call_id = Column(String(100), nullable=True)


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), index=True, nullable=True)
    rating = Column(Integer, nullable=False)
    feedback_text = Column(Text, nullable=False)
    phone_number = Column(String(15), nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    call_id = Column(String(100), nullable=True)


class Emergency(Base):
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
