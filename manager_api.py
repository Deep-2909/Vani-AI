"""
Manager API - Backend functionality for government officials
Handles complaint resolution, area hotspot monitoring, and outbound campaigns
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from sqlalchemy import text, func
from app.db import engine

router = APIRouter(prefix="/manager", tags=["Manager"])

# ===================================================================
# REQUEST/RESPONSE MODELS
# ===================================================================

class ResolveComplaintRequest(BaseModel):
    ticket_id: str
    resolved_by: str  # Manager name
    resolution_notes: str
    citizen_rating: Optional[int] = None

class BulkResolveRequest(BaseModel):
    ticket_ids: List[str]
    resolved_by: str
    resolution_notes: str

class AreaHotspotResponse(BaseModel):
    area_name: str
    total_complaints: int
    open_complaints: int
    is_hotspot: bool
    hotspot_level: Optional[str]
    last_complaint_at: Optional[datetime]

class OutboundCallRequest(BaseModel):
    phone_numbers: List[str]
    call_type: str  # scheme_notification, alert, follow_up
    message_content: str
    language: str = "hindi"
    scheme_name: Optional[str] = None
    alert_type: Optional[str] = None

class SchemeNotificationRequest(BaseModel):
    scheme_code: str
    target_areas: Optional[List[str]] = None
    language: str = "hindi"


# ===================================================================
# COMPLAINT RESOLUTION ENDPOINTS
# ===================================================================

@router.post("/resolve-complaint")
async def resolve_complaint(request: ResolveComplaintRequest):
    """
    Transfer a complaint from grievances to complaints_resolved table.
    This marks the complaint as resolved and archives it.
    """
    try:
        with engine.begin() as conn:
            # 1. Fetch the complaint
            result = conn.execute(
                text("""
                    SELECT 
                        ticket_id, citizen_name, contact, description, location, area,
                        department, category, priority, call_id, language,
                        created_at, resolved_at
                    FROM grievances 
                    WHERE ticket_id = :ticket_id AND status != 'RESOLVED'
                """),
                {"ticket_id": request.ticket_id}
            )
            
            complaint = result.fetchone()
            
            if not complaint:
                raise HTTPException(status_code=404, detail="Complaint not found or already resolved")
            
            # 2. Calculate resolution time
            created_at = complaint[11]
            resolved_at = complaint[12] or datetime.now()
            resolution_hours = (resolved_at - created_at).total_seconds() / 3600
            
            # 3. Insert into complaints_resolved
            conn.execute(
                text("""
                    INSERT INTO complaints_resolved 
                    (ticket_id, citizen_name, contact, description, location, area,
                     department, category, priority, call_id,
                     complaint_created_at, complaint_resolved_at, resolution_time_hours,
                     resolved_by, resolution_notes, citizen_rating, transferred_by)
                    VALUES 
                    (:ticket_id, :name, :contact, :description, :location, :area,
                     :department, :category, :priority, :call_id,
                     :created_at, :resolved_at, :resolution_hours,
                     :resolved_by, :notes, :rating, :transferred_by)
                """),
                {
                    "ticket_id": complaint[0],
                    "name": complaint[1],
                    "contact": complaint[2],
                    "description": complaint[3],
                    "location": complaint[4],
                    "area": complaint[5],
                    "department": complaint[6],
                    "category": complaint[7],
                    "priority": complaint[8],
                    "call_id": complaint[9],
                    "created_at": created_at,
                    "resolved_at": resolved_at,
                    "resolution_hours": resolution_hours,
                    "resolved_by": request.resolved_by,
                    "notes": request.resolution_notes,
                    "rating": request.citizen_rating,
                    "transferred_by": request.resolved_by
                }
            )
            
            # 4. Delete from grievances table
            conn.execute(
                text("DELETE FROM grievances WHERE ticket_id = :ticket_id"),
                {"ticket_id": request.ticket_id}
            )
            
            # 5. Update area hotspot stats
            if complaint[5]:  # if area exists
                conn.execute(
                    text("""
                        UPDATE area_hotspots 
                        SET open_complaints = open_complaints - 1,
                            resolved_complaints = resolved_complaints + 1,
                            last_updated = NOW()
                        WHERE area_name = :area
                    """),
                    {"area": complaint[5]}
                )
        
        return {
            "success": True,
            "message": f"Complaint {request.ticket_id} resolved and archived",
            "resolution_time_hours": round(resolution_hours, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving complaint: {str(e)}")


@router.post("/bulk-resolve")
async def bulk_resolve_complaints(request: BulkResolveRequest):
    """
    Resolve multiple complaints at once.
    Useful for batch processing.
    """
    resolved = []
    failed = []
    
    for ticket_id in request.ticket_ids:
        try:
            result = await resolve_complaint(ResolveComplaintRequest(
                ticket_id=ticket_id,
                resolved_by=request.resolved_by,
                resolution_notes=request.resolution_notes
            ))
            resolved.append(ticket_id)
        except:
            failed.append(ticket_id)
    
    return {
        "success": True,
        "resolved_count": len(resolved),
        "failed_count": len(failed),
        "resolved_tickets": resolved,
        "failed_tickets": failed
    }


@router.get("/resolved-complaints")
async def get_resolved_complaints(
    limit: int = 50,
    offset: int = 0,
    department: Optional[str] = None
):
    """
    Get list of resolved complaints with pagination.
    """
    try:
        with engine.connect() as conn:
            query = """
                SELECT 
                    ticket_id, citizen_name, department, category, priority,
                    complaint_created_at, resolution_date, resolution_time_hours,
                    resolved_by, citizen_rating
                FROM complaints_resolved
            """
            
            params = {"limit": limit, "offset": offset}
            
            if department:
                query += " WHERE department = :department"
                params["department"] = department
            
            query += " ORDER BY resolution_date DESC LIMIT :limit OFFSET :offset"
            
            result = conn.execute(text(query), params)
            
            complaints = [
                {
                    "ticket_id": row[0],
                    "citizen_name": row[1],
                    "department": row[2],
                    "category": row[3],
                    "priority": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                    "resolved_at": row[6].isoformat() if row[6] else None,
                    "resolution_hours": round(row[7], 2) if row[7] else None,
                    "resolved_by": row[8],
                    "rating": row[9]
                }
                for row in result
            ]
            
            return {"complaints": complaints, "count": len(complaints)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# AREA HOTSPOT MONITORING
# ===================================================================

@router.get("/area-hotspots")
async def get_area_hotspots(
    flagged_only: bool = False,
    min_complaints: int = 5
):
    """
    Get areas with high complaint density.
    Helps identify problem areas that need immediate attention.
    """
    try:
        with engine.connect() as conn:
            query = """
                SELECT 
                    area_name, total_complaints, open_complaints, resolved_complaints,
                    is_hotspot, hotspot_level, last_complaint_at,
                    water_complaints, road_complaints, electricity_complaints,
                    critical_complaints, high_complaints
                FROM area_hotspots
                WHERE total_complaints >= :min_complaints
            """
            
            params = {"min_complaints": min_complaints}
            
            if flagged_only:
                query += " AND is_hotspot = TRUE"
            
            query += " ORDER BY open_complaints DESC, total_complaints DESC"
            
            result = conn.execute(text(query), params)
            
            hotspots = [
                {
                    "area_name": row[0],
                    "total_complaints": row[1],
                    "open_complaints": row[2],
                    "resolved_complaints": row[3],
                    "is_hotspot": row[4],
                    "hotspot_level": row[5],
                    "last_complaint_at": row[6].isoformat() if row[6] else None,
                    "breakdown": {
                        "water": row[7],
                        "road": row[8],
                        "electricity": row[9]
                    },
                    "priority_breakdown": {
                        "critical": row[10],
                        "high": row[11]
                    }
                }
                for row in result
            ]
            
            return {"hotspots": hotspots, "count": len(hotspots)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/area-details/{area_name}")
async def get_area_details(area_name: str):
    """
    Get detailed complaint breakdown for a specific area.
    """
    try:
        with engine.connect() as conn:
            # Get area stats
            result = conn.execute(
                text("SELECT * FROM area_hotspots WHERE area_name = :area"),
                {"area": area_name}
            )
            area_stats = result.fetchone()
            
            if not area_stats:
                raise HTTPException(status_code=404, detail="Area not found")
            
            # Get recent complaints from this area
            result = conn.execute(
                text("""
                    SELECT ticket_id, category, priority, status, created_at
                    FROM grievances
                    WHERE area = :area
                    ORDER BY created_at DESC
                    LIMIT 20
                """),
                {"area": area_name}
            )
            
            recent_complaints = [
                {
                    "ticket_id": row[0],
                    "category": row[1],
                    "priority": row[2],
                    "status": row[3],
                    "created_at": row[4].isoformat() if row[4] else None
                }
                for row in result
            ]
            
            return {
                "area_name": area_name,
                "stats": {
                    "total_complaints": area_stats[2],
                    "open": area_stats[3],
                    "resolved": area_stats[4],
                    "is_hotspot": area_stats[10],
                    "hotspot_level": area_stats[11]
                },
                "recent_complaints": recent_complaints
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# OUTBOUND CALL MANAGEMENT
# ===================================================================

@router.post("/initiate-outbound-calls")
async def initiate_outbound_calls(request: OutboundCallRequest):
    """
    Initiate outbound calls for schemes, alerts, or follow-ups.
    This creates call records that will be processed by Retell.
    """
    try:
        call_ids = []
        
        with engine.begin() as conn:
            for phone_number in request.phone_numbers:
                call_id = f"OUT-{uuid.uuid4().hex[:10].upper()}"
                
                conn.execute(
                    text("""
                        INSERT INTO outbound_calls
                        (call_id, phone_number, call_type, message_content,
                         scheme_name, alert_type, status, initiated_at, 
                         initiated_by, language)
                        VALUES
                        (:call_id, :phone, :type, :message,
                         :scheme, :alert, 'PENDING', NOW(),
                         'SYSTEM', :language)
                    """),
                    {
                        "call_id": call_id,
                        "phone": phone_number,
                        "type": request.call_type,
                        "message": request.message_content,
                        "scheme": request.scheme_name,
                        "alert": request.alert_type,
                        "language": request.language
                    }
                )
                
                call_ids.append(call_id)
        
        return {
            "success": True,
            "message": f"Initiated {len(call_ids)} outbound calls",
            "call_ids": call_ids
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notify-scheme")
async def notify_scheme_to_areas(request: SchemeNotificationRequest):
    """
    Send scheme notifications to citizens in specific areas.
    Automatically creates outbound calls for eligible citizens.
    """
    try:
        with engine.connect() as conn:
            # Get scheme details
            result = conn.execute(
                text("SELECT * FROM government_schemes WHERE scheme_code = :code AND is_active = TRUE"),
                {"code": request.scheme_code}
            )
            scheme = result.fetchone()
            
            if not scheme:
                raise HTTPException(status_code=404, detail="Scheme not found or inactive")
            
            # Get phone numbers from target areas
            query = """
                SELECT DISTINCT contact 
                FROM grievances 
                WHERE contact IS NOT NULL
            """
            
            params = {}
            
            if request.target_areas:
                placeholders = ','.join([f':area{i}' for i in range(len(request.target_areas))])
                query += f" AND area IN ({placeholders})"
                params = {f'area{i}': area for i, area in enumerate(request.target_areas)}
            
            result = conn.execute(text(query), params)
            phone_numbers = [row[0] for row in result if row[0]]
            
            # Create outbound calls
            if phone_numbers:
                notification = await initiate_outbound_calls(OutboundCallRequest(
                    phone_numbers=phone_numbers,
                    call_type="scheme_notification",
                    message_content=scheme[9],  # notification_message
                    language=request.language,
                    scheme_name=scheme[2]  # scheme_name
                ))
                
                return {
                    "success": True,
                    "scheme_name": scheme[2],
                    "notifications_sent": len(phone_numbers),
                    "call_ids": notification["call_ids"]
                }
            else:
                return {
                    "success": False,
                    "message": "No eligible citizens found in target areas"
                }
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outbound-calls/status")
async def get_outbound_call_status(
    call_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """
    Get status of outbound calls.
    """
    try:
        with engine.connect() as conn:
            query = """
                SELECT call_id, phone_number, call_type, status, 
                       initiated_at, completed_at, answered, language
                FROM outbound_calls
                WHERE 1=1
            """
            
            params = {"limit": limit}
            
            if call_type:
                query += " AND call_type = :call_type"
                params["call_type"] = call_type
            
            if status:
                query += " AND status = :status"
                params["status"] = status
            
            query += " ORDER BY initiated_at DESC LIMIT :limit"
            
            result = conn.execute(text(query), params)
            
            calls = [
                {
                    "call_id": row[0],
                    "phone_number": row[1],
                    "call_type": row[2],
                    "status": row[3],
                    "initiated_at": row[4].isoformat() if row[4] else None,
                    "completed_at": row[5].isoformat() if row[5] else None,
                    "answered": row[6],
                    "language": row[7]
                }
                for row in result
            ]
            
            return {"calls": calls, "count": len(calls)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# ANALYTICS & REPORTS
# ===================================================================

@router.get("/dashboard-stats")
async def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics for managers.
    """
    try:
        with engine.connect() as conn:
            # Total complaints
            result = conn.execute(text("SELECT COUNT(*) FROM grievances"))
            total_open = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) FROM complaints_resolved"))
            total_resolved = result.fetchone()[0]
            
            # By priority
            result = conn.execute(text("""
                SELECT priority, COUNT(*) 
                FROM grievances 
                GROUP BY priority
            """))
            by_priority = {row[0]: row[1] for row in result}
            
            # By department
            result = conn.execute(text("""
                SELECT department, COUNT(*) 
                FROM grievances 
                GROUP BY department 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            """))
            by_department = {row[0]: row[1] for row in result}
            
            # Hotspots
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM area_hotspots 
                WHERE is_hotspot = TRUE
            """))
            total_hotspots = result.fetchone()[0]
            
            # Average resolution time
            result = conn.execute(text("""
                SELECT AVG(resolution_time_hours) 
                FROM complaints_resolved 
                WHERE resolution_date > NOW() - INTERVAL '30 days'
            """))
            avg_resolution_hours = result.fetchone()[0] or 0
            
            return {
                "total_open_complaints": total_open,
                "total_resolved_complaints": total_resolved,
                "by_priority": by_priority,
                "top_departments": by_department,
                "active_hotspots": total_hotspots,
                "avg_resolution_hours": round(avg_resolution_hours, 2)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
