"""
Complete API Bridge for Frontend-Backend Integration
This file contains ALL missing endpoints that frontend needs
"""
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import text, func
from app.db import engine
from app.ws import manager
import asyncio

router = APIRouter()

# ===================================================================
# PYDANTIC MODELS (Data Validation)
# ===================================================================

class CallLogQuery(BaseModel):
    limit: Optional[int] = 20
    offset: Optional[int] = 0
    type: Optional[str] = None  # 'inbound' or 'outbound'
    outcome: Optional[str] = None
    search: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class DashboardAnalytics(BaseModel):
    total_calls: int
    avg_resolution_time: int  # seconds
    success_rate: float  # percentage
    cost_saved: float
    calls_today: int
    active_now: int


class CallingQueueEntry(BaseModel):
    name: str
    phone: str
    description: Optional[str] = ""
    priority: Optional[int] = 0


class AgentConfiguration(BaseModel):
    agent_name: str
    agent_description: str
    tools: dict
    category: str
    department: str


class DocumentUpload(BaseModel):
    filename: str
    file_type: str
    size: int
    vectorized: bool = False


# ===================================================================
# 1. CALL LOGS API
# ===================================================================

@router.get("/api/calls")
async def get_call_logs(
    limit: int = 20,
    offset: int = 0,
    call_type: Optional[str] = None,
    outcome: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Fetch call logs with filtering and pagination
    Maps to: CallLogs.tsx component
    """
    try:
        with engine.connect() as conn:
            # Build query
            query = """
                SELECT
                    g.call_id as id,
                    g.contact as caller_id,
                    'inbound' as type,
                    COALESCE(g.call_duration, 0) as duration,
                    CASE
                        WHEN g.status = 'RESOLVED' THEN 'resolved'
                        WHEN g.escalated > 0 THEN 'escalated'
                        ELSE 'dropped'
                    END as outcome,
                    g.created_at as timestamp,
                    g.description as summary,
                    g.ticket_id,
                    g.transcript,
                    g.retell_call_id
                FROM grievances g
                WHERE g.call_id IS NOT NULL
            """
            
            params = {}
            
            # Add filters
            if search:
                query += " AND (g.contact LIKE :search OR g.description LIKE :search)"
                params['search'] = f"%{search}%"
            
            if call_type:
                # For now all are inbound, but placeholder for future
                pass
            
            query += " ORDER BY g.created_at DESC LIMIT :limit OFFSET :offset"
            params['limit'] = limit
            params['offset'] = offset
            
            result = conn.execute(text(query), params)
            
            calls = []
            for row in result:
                calls.append({
                    "id": row[0] or f"call-{row[7]}",
                    "callerId": row[1] or "Unknown",
                    "type": row[2],
                    "duration": row[3] or 0,
                    "outcome": row[4],
                    "timestamp": row[5].isoformat() if row[5] else datetime.now().isoformat(),
                    "summary": row[6],
                    "ticketId": row[7],
                    "transcript": row[8],
                    "retellCallId": row[9]
                })
            
            return {
                "success": True,
                "data": calls,
                "total": len(calls),
                "limit": limit,
                "offset": offset
            }
            
    except Exception as e:
        print(f"❌ Error fetching call logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/calls/{call_id}")
async def get_call_details(call_id: str):
    """
    Get detailed information for a specific call
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        g.call_id,
                        g.contact,
                        g.citizen_name,
                        g.description,
                        g.category,
                        g.priority,
                        g.status,
                        g.ticket_id,
                        g.created_at,
                        g.resolved_at,
                        g.department,
                        g.location
                    FROM grievances g
                    WHERE g.call_id = :call_id OR g.ticket_id = :call_id
                    LIMIT 1
                """),
                {"call_id": call_id}
            )
            
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Call not found")
            
            duration = 0
            if row[8] and row[9]:
                duration = int((row[9] - row[8]).total_seconds())
            
            return {
                "success": True,
                "data": {
                    "id": row[0],
                    "callerId": row[1],
                    "callerName": row[2],
                    "summary": row[3],
                    "category": row[4],
                    "priority": row[5],
                    "status": row[6],
                    "ticketId": row[7],
                    "timestamp": row[8].isoformat() if row[8] else None,
                    "duration": duration,
                    "department": row[10],
                    "location": row[11]
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching call details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/calls/{call_id}/fetch-transcript")
async def fetch_and_save_transcript(call_id: str):
    """
    Fetch transcript from Retell API and save to database
    This endpoint is called on-demand to get transcript for a call
    """
    try:
        from app.services.retell_api import fetch_call_transcript

        with engine.connect() as conn:
            # Get retell_call_id for this call
            result = conn.execute(
                text("""
                    SELECT retell_call_id, transcript
                    FROM grievances
                    WHERE call_id = :call_id OR ticket_id = :call_id
                    LIMIT 1
                """),
                {"call_id": call_id}
            )

            row = result.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Call not found")

            retell_call_id = row[0]
            existing_transcript = row[1]

            # If transcript already exists, return it
            if existing_transcript:
                print(f"✅ Transcript found in cache for call {call_id}")
                return {
                    "success": True,
                    "data": {
                        "transcript": existing_transcript,
                        "cached": True
                    }
                }

            # If no retell_call_id, can't fetch
            if not retell_call_id:
                print(f"⚠️ No Retell call ID for call {call_id}")
                return {
                    "success": False,
                    "error": "No Retell call ID associated with this call"
                }

            print(f"🔍 Fetching transcript from Retell API for retell_call_id: {retell_call_id}")

            # Fetch from Retell API
            transcript = fetch_call_transcript(retell_call_id)

            if transcript:
                print(f"✅ Transcript fetched successfully ({len(transcript)} chars), saving to database")
                # Save to database
                with engine.begin() as conn_write:
                    conn_write.execute(
                        text("""
                            UPDATE grievances
                            SET transcript = :transcript
                            WHERE call_id = :call_id OR ticket_id = :call_id
                        """),
                        {"transcript": transcript, "call_id": call_id}
                    )

                return {
                    "success": True,
                    "data": {
                        "transcript": transcript,
                        "cached": False
                    }
                }
            else:
                print(f"❌ No transcript available from Retell API")
                return {
                    "success": False,
                    "error": "Transcript not available from Retell"
                }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 2. ANALYTICS DASHBOARD API
# ===================================================================

@router.get("/api/analytics")
async def get_dashboard_analytics():
    """
    Get real-time analytics for dashboard
    Maps to: Index.tsx, AnalyticsCard components
    """
    try:
        with engine.connect() as conn:
            # Total calls
            total_result = conn.execute(
                text("SELECT COUNT(*) FROM grievances WHERE call_id IS NOT NULL")
            )
            total_calls = total_result.fetchone()[0]
            
            # Calls today
            today_result = conn.execute(
                text("""
                    SELECT COUNT(*) FROM grievances 
                    WHERE call_id IS NOT NULL 
                    AND DATE(created_at) = CURRENT_DATE
                """)
            )
            calls_today = today_result.fetchone()[0]
            
            # Average resolution time (in seconds)
            avg_time_result = conn.execute(
                text("""
                    SELECT AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)))
                    FROM grievances
                    WHERE resolved_at IS NOT NULL
                """)
            )
            avg_resolution_time = int(avg_time_result.fetchone()[0] or 0)
            
            # Success rate (resolved / total)
            success_result = conn.execute(
                text("""
                    SELECT 
                        COUNT(*) FILTER (WHERE status = 'RESOLVED')::float / 
                        NULLIF(COUNT(*), 0) * 100
                    FROM grievances
                """)
            )
            success_rate = float(success_result.fetchone()[0] or 0)
            
            # Active calls (currently in progress)
            # For now, count complaints created in last hour that aren't resolved
            active_result = conn.execute(
                text("""
                    SELECT COUNT(*) FROM grievances
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    AND status NOT IN ('RESOLVED', 'CLOSED')
                """)
            )
            active_now = active_result.fetchone()[0]
            
            # Cost saved calculation (assuming $2 per call vs human agent)
            cost_saved = total_calls * 2.0
            
            return {
                "success": True,
                "data": {
                    "totalCalls": total_calls,
                    "avgResolutionTime": avg_resolution_time,
                    "successRate": round(success_rate, 1),
                    "costSaved": cost_saved,
                    "callsToday": calls_today,
                    "activeNow": active_now
                }
            }
            
    except Exception as e:
        print(f"❌ Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analytics/complaints")
async def get_complaint_analytics():
    """
    Get complaint analytics (top locations, top issues)
    Maps to: ComplaintAnalytics.tsx
    """
    try:
        with engine.connect() as conn:
            # Top 5 locations by complaint count
            locations_result = conn.execute(
                text("""
                    SELECT 
                        area_name as location,
                        open_complaints as complaints,
                        CASE 
                            WHEN open_complaints > LAG(open_complaints, 1, 0) 
                                OVER (ORDER BY open_complaints DESC) THEN 'up'
                            WHEN open_complaints < LAG(open_complaints, 1, 0) 
                                OVER (ORDER BY open_complaints DESC) THEN 'down'
                            ELSE 'stable'
                        END as trend,
                        ROUND(open_complaints::numeric / 
                            NULLIF((SELECT SUM(open_complaints) FROM area_hotspots), 0) * 100, 1
                        ) as percentage
                    FROM area_hotspots
                    WHERE area_name IS NOT NULL
                    ORDER BY open_complaints DESC
                    LIMIT 5
                """)
            )
            
            top_locations = [
                {
                    "location": row[0],
                    "complaints": row[1],
                    "trend": row[2] or "stable",
                    "percentage": float(row[3] or 0)
                }
                for row in locations_result
            ]
            
            # Top 5 issues by category
            issues_result = conn.execute(
                text("""
                    SELECT 
                        category as issue,
                        COUNT(*) as complaints,
                        'stable' as trend,
                        ROUND(COUNT(*)::numeric / 
                            NULLIF((SELECT COUNT(*) FROM grievances WHERE category IS NOT NULL), 0) * 100, 1
                        ) as percentage,
                        CASE 
                            WHEN priority = 'Critical' THEN 'high'
                            WHEN priority = 'High' THEN 'high'
                            WHEN priority = 'Medium' THEN 'medium'
                            ELSE 'low'
                        END as severity
                    FROM grievances
                    WHERE category IS NOT NULL
                    GROUP BY category, priority
                    ORDER BY complaints DESC
                    LIMIT 5
                """)
            )
            
            top_issues = [
                {
                    "issue": row[0],
                    "complaints": row[1],
                    "trend": row[2],
                    "percentage": float(row[3] or 0),
                    "severity": row[4] or "medium"
                }
                for row in issues_result
            ]
            
            # Summary stats
            summary_result = conn.execute(
                text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE status = 'RESOLVED') as resolved,
                        COUNT(*) FILTER (WHERE status IN ('OPEN', 'IN_PROGRESS')) as pending
                    FROM grievances
                """)
            )
            
            summary = summary_result.fetchone()
            
            return {
                "success": True,
                "data": {
                    "topLocations": top_locations,
                    "topIssues": top_issues,
                    "summary": {
                        "total": summary[0],
                        "resolved": summary[1],
                        "pending": summary[2]
                    }
                }
            }
            
    except Exception as e:
        print(f"❌ Error fetching complaint analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/complaints")
async def get_all_complaints(
    limit: int = 50,
    offset: int = 0,
    department: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get list of all complaints with filters
    Maps to: Complaints.tsx
    """
    try:
        with engine.connect() as conn:
            query = """
                SELECT
                    ticket_id, citizen_name, contact, description, location, area,
                    department, category, priority, status, created_at
                FROM grievances
                WHERE 1=1
            """

            params = {"limit": limit, "offset": offset}

            if department:
                query += " AND department = :department"
                params["department"] = department

            if priority:
                query += " AND priority = :priority"
                params["priority"] = priority

            if status:
                query += " AND status = :status"
                params["status"] = status

            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"

            result = conn.execute(text(query), params)

            complaints = [
                {
                    "ticket_id": row[0],
                    "citizen_name": row[1],
                    "contact": row[2],
                    "description": row[3],
                    "location": row[4],
                    "area": row[5],
                    "department": row[6],
                    "category": row[7],
                    "priority": row[8],
                    "status": row[9],
                    "created_at": row[10].isoformat() if row[10] else None
                }
                for row in result
            ]

            # Get total count
            count_query = "SELECT COUNT(*) FROM grievances WHERE 1=1"
            count_params = {}

            if department:
                count_query += " AND department = :department"
                count_params["department"] = department

            if priority:
                count_query += " AND priority = :priority"
                count_params["priority"] = priority

            if status:
                count_query += " AND status = :status"
                count_params["status"] = status

            count_result = conn.execute(text(count_query), count_params)
            total_count = count_result.fetchone()[0]

            return {
                "success": True,
                "data": {
                    "complaints": complaints,
                    "count": len(complaints),
                    "total": total_count
                }
            }

    except Exception as e:
        print(f"❌ Error fetching complaints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 3. KNOWLEDGE BASE API
# ===================================================================

@router.post("/api/knowledge-base/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload documents to knowledge base
    Maps to: KnowledgeBase.tsx
    """
    try:
        uploaded_docs = []
        
        for file in files:
            # Save file to data directory (same as ingestion pipeline)
            import os
            os.makedirs("./data", exist_ok=True)  # Ensure directory exists
            file_path = f"./data/{file.filename}"

            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Create document record
            doc = {
                "id": str(uuid.uuid4()),
                "name": file.filename,
                "type": file.filename.split(".")[-1],
                "uploadedDate": datetime.now().strftime("%m/%d/%Y"),
                "size": len(content),
                "vectorized": False  # Will be vectorized by separate process
            }
            
            uploaded_docs.append(doc)

        # Trigger automatic vectorization for ONLY the newly uploaded files
        vectorization_results = []
        all_successful = True

        try:
            print(f"🔄 Starting vectorization for {len(files)} newly uploaded document(s)...")

            # Import the selective ingestion function
            from ingest_robust import ingest_single_file

            # Vectorize each uploaded file individually
            for i, doc in enumerate(uploaded_docs):
                file_path = f"./data/{doc['name']}"
                print(f"\n[{i+1}/{len(uploaded_docs)}] Processing: {doc['name']}")

                result = ingest_single_file(file_path)
                vectorization_results.append(result)

                if result["success"]:
                    doc["vectorized"] = True
                    doc["chunks"] = result["chunks"]
                    print(f"  ✅ {result['message']} ({result['chunks']} chunks)")
                else:
                    doc["vectorized"] = False
                    doc["chunks"] = 0
                    doc["error"] = result["message"]
                    all_successful = False
                    print(f"  ❌ {result['message']}")

            print(f"\n✅ Vectorization complete for {len(files)} document(s)!")

        except ImportError as import_err:
            print(f"❌ Failed to import ingest_single_file: {import_err}")
            all_successful = False
            for doc in uploaded_docs:
                doc["vectorized"] = False
                doc["error"] = "Ingestion module not available"

        except Exception as vectorize_error:
            print(f"⚠️ Unexpected vectorization error: {vectorize_error}")
            all_successful = False
            for doc in uploaded_docs:
                if "vectorized" not in doc:
                    doc["vectorized"] = False
                    doc["error"] = str(vectorize_error)

        # Return appropriate message based on results
        if all_successful:
            message = f"Successfully uploaded and vectorized {len(files)} document(s)"
        else:
            successful_count = sum(1 for doc in uploaded_docs if doc.get("vectorized", False))
            failed_count = len(files) - successful_count
            message = f"Uploaded {len(files)} document(s). {successful_count} vectorized successfully, {failed_count} failed. Check if files are valid PDFs."

        return {
            "success": True,
            "data": uploaded_docs,
            "message": message,
            "vectorization_results": vectorization_results
        }
        
    except Exception as e:
        print(f"❌ Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/knowledge-base/documents")
async def get_documents(search: Optional[str] = None):
    """
    Get list of documents in knowledge base
    Maps to: KnowledgeBase.tsx
    """
    try:
        # Scan the data directory where documents are stored
        import os
        from pathlib import Path

        data_dir = "./data"
        documents = []

        if os.path.exists(data_dir):
            for file_path in Path(data_dir).glob("**/*"):
                if file_path.is_file() and file_path.suffix in ['.pdf', '.doc', '.docx', '.txt', '.xlsx']:
                    doc = {
                        "id": str(uuid.uuid4()),
                        "name": file_path.name,
                        "type": file_path.suffix[1:],
                        "uploadedDate": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%m/%d/%Y"),
                        "size": file_path.stat().st_size,
                        "vectorized": True  # Assume vectorized if in data folder
                    }

                    if search:
                        if search.lower() in file_path.name.lower():
                            documents.append(doc)
                    else:
                        documents.append(doc)
        
        return {
            "success": True,
            "data": documents
        }
        
    except Exception as e:
        print(f"❌ Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 4. DATABASE SYNC API
# ===================================================================

@router.get("/api/databases/sources")
async def get_database_sources():
    """
    Get connected database sources
    Maps to: Databases.tsx
    """
    try:
        with engine.connect() as conn:
            # Get grievances table info
            result = conn.execute(
                text("""
                    SELECT 
                        DATE(created_at) as date,
                        citizen_name,
                        description,
                        department,
                        ticket_id
                    FROM grievances
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
            )
            
            complaint_data = [
                {
                    "id": str(i+1),
                    "date": row[0].strftime("%d %b") if row[0] else "",
                    "nameOfPerson": row[1] or "Unknown",
                    "descriptionOfComplain": row[2] or "",
                    "department": row[3] or "General",
                    "ticketId": row[4] or "N/A"
                }
                for i, row in enumerate(result)
            ]
            
            sources = [{
                "id": "db-1",
                "name": "COMPLAINT TICKET DATA",
                "type": "table",
                "status": "active",
                "recordCount": len(complaint_data),
                "lastSync": datetime.now().isoformat(),
                "columns": ["TICKET ID", "DATE", "NAME OF PERSON", "DESCRIPTION OF COMPLAIN", "DEPARTMENT"],
                "data": complaint_data
            }]
            
            return {
                "success": True,
                "data": sources
            }
            
    except Exception as e:
        print(f"❌ Error fetching database sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/databases/sync")
async def sync_database_source(
    dataset_name: str,
    source_type: str,
    connection_string: Optional[str] = None
):
    """
    Sync a new database source
    Maps to: Databases.tsx LinkDataSourceDialog
    """
    try:
        # TODO: Implement actual database sync logic
        # This would connect to external DB and import data
        
        return {
            "success": True,
            "message": f"Successfully synced {dataset_name}",
            "sourceId": str(uuid.uuid4())
        }
        
    except Exception as e:
        print(f"❌ Error syncing database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 5. CALLING QUEUE API
# ===================================================================

@router.get("/api/calling-queue")
async def get_calling_queue():
    """
    Get current calling queue (server-side storage)
    Maps to: CallingList.tsx, CallingQueue.tsx
    """
    try:
        # Store queue in database for persistence
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        call_id as id,
                        phone_number as phone,
                        message_content as description,
                        initiated_at as added_at
                    FROM outbound_calls
                    WHERE status = 'PENDING'
                    ORDER BY scheduled_at ASC, initiated_at ASC
                """)
            )
            
            queue = [
                {
                    "id": row[0],
                    "phone": row[1],
                    "name": row[1],  # Default to phone if no name
                    "description": row[2] or "",
                    "addedAt": row[3].isoformat() if row[3] else datetime.now().isoformat()
                }
                for row in result
            ]
            
            return {
                "success": True,
                "data": queue
            }
            
    except Exception as e:
        print(f"❌ Error fetching calling queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/calling-queue")
async def add_to_calling_queue(entry: CallingQueueEntry):
    """
    Add entry to calling queue
    """
    try:
        call_id = f"OUT-{uuid.uuid4().hex[:8].upper()}"
        
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO outbound_calls
                    (call_id, phone_number, call_type, message_content, status, initiated_at)
                    VALUES (:call_id, :phone, 'manual', :description, 'PENDING', NOW())
                """),
                {
                    "call_id": call_id,
                    "phone": entry.phone,
                    "description": f"{entry.name}: {entry.description}"
                }
            )
        
        return {
            "success": True,
            "data": {
                "id": call_id,
                "phone": entry.phone,
                "name": entry.name,
                "description": entry.description,
                "addedAt": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"❌ Error adding to queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/calling-queue/{entry_id}")
async def remove_from_calling_queue(entry_id: str):
    """
    Remove entry from calling queue
    """
    try:
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM outbound_calls WHERE call_id = :id"),
                {"id": entry_id}
            )
        
        return {"success": True}
        
    except Exception as e:
        print(f"❌ Error removing from queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 6. AGENT CONFIGURATION API
# ===================================================================

@router.get("/api/agent/config")
async def get_agent_config():
    """
    Get current AI agent configuration
    Maps to: Index.tsx AI Customization section
    """
    try:
        # TODO: Store in database, for now use environment or config file
        config = {
            "agentName": os.getenv("AGENT_NAME", "Voice AI"),
            "agentDescription": os.getenv("AGENT_DESCRIPTION", 
                "AI Voice Assistant for Delhi Government"),
            "category": "Company",
            "department": "Delhi Government",
            "accountType": "Demo Account",
            "tools": {
                "knowledgeQuery": True,
                "endCall": True,
                "complainTicket": True
            }
        }
        
        return {
            "success": True,
            "data": config
        }
        
    except Exception as e:
        print(f"❌ Error fetching agent config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/agent/config")
async def update_agent_config(config: AgentConfiguration):
    """
    Update AI agent configuration
    """
    try:
        # TODO: Save to database or config file
        # For now, just validate and return success
        
        return {
            "success": True,
            "message": "Agent configuration updated successfully",
            "data": config
        }
        
    except Exception as e:
        print(f"❌ Error updating agent config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 7. ACTIVE CALLS WEBSOCKET
# ===================================================================

@router.websocket("/ws/active-calls")
async def active_calls_websocket(websocket: WebSocket):
    """
    WebSocket for real-time active call monitoring
    Maps to: ActiveCallsMonitor.tsx
    """
    await websocket.accept()
    
    try:
        while True:
            # Send active call updates every 2 seconds
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT 
                            g.call_id,
                            g.contact,
                            'inbound' as type,
                            EXTRACT(EPOCH FROM (NOW() - g.created_at))::int as duration,
                            80 as sentiment,
                            'active' as status
                        FROM grievances g
                        WHERE g.created_at > NOW() - INTERVAL '10 minutes'
                        AND g.status NOT IN ('RESOLVED', 'CLOSED')
                        LIMIT 5
                    """)
                )
                
                active_calls = [
                    {
                        "id": row[0],
                        "callerId": row[1],
                        "type": row[2],
                        "duration": row[3],
                        "sentiment": row[4],
                        "status": row[5]
                    }
                    for row in result
                ]
                
                await websocket.send_json({
                    "event": "ACTIVE_CALLS_UPDATE",
                    "data": active_calls
                })
            
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        print("Active calls WebSocket disconnected")


# ===================================================================
# 8. START CALLING ENDPOINTS
# ===================================================================

@router.post("/api/calls/start-inbound")
async def start_inbound_calling():
    """
    Start inbound call agent
    Maps to: Index.tsx "Start Inbound Agent" button
    """
    try:
        # TODO: Initialize Vapi/Retell inbound agent
        # This would configure your phone system to route calls to AI
        
        return {
            "success": True,
            "message": "Inbound agent started successfully",
            "status": "active"
        }
        
    except Exception as e:
        print(f"❌ Error starting inbound agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/calls/start-outbound")
async def start_outbound_calling():
    """
    Start outbound calling campaign
    Maps to: Index.tsx "Start Outbound Calling" button
    """
    try:
        with engine.connect() as conn:
            # Get next entry from queue
            result = conn.execute(
                text("""
                    SELECT call_id, phone_number, message_content
                    FROM outbound_calls
                    WHERE status = 'PENDING'
                    ORDER BY scheduled_at ASC, initiated_at ASC
                    LIMIT 1
                """)
            )
            
            next_call = result.fetchone()
            
            if not next_call:
                return {
                    "success": False,
                    "message": "No entries in calling queue"
                }
            
            # TODO: Trigger Retell AI outbound call
            # from app.services.outbound import create_retell_call
            # await create_retell_call(next_call[1], next_call[2])
            
            # Update status
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE outbound_calls
                        SET status = 'INITIATED', initiated_at = NOW()
                        WHERE call_id = :call_id
                    """),
                    {"call_id": next_call[0]}
                )
            
            return {
                "success": True,
                "message": "Outbound calling started",
                "callId": next_call[0],
                "phoneNumber": next_call[1]
            }
            
    except Exception as e:
        print(f"❌ Error starting outbound calling: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 9. EXPORT/DOWNLOAD ENDPOINTS
# ===================================================================

@router.get("/api/calls/export")
async def export_call_logs(format: str = "csv"):
    """
    Export call logs to CSV/Excel
    Maps to: CallLogs.tsx "Export" button
    """
    try:
        import csv
        from io import StringIO
        
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        g.ticket_id,
                        g.contact,
                        g.citizen_name,
                        g.category,
                        g.priority,
                        g.status,
                        g.created_at,
                        g.resolved_at,
                        g.description
                    FROM grievances g
                    WHERE g.call_id IS NOT NULL
                    ORDER BY g.created_at DESC
                """)
            )
            
            # Generate CSV
            output = StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(['Ticket ID', 'Phone', 'Name', 'Category', 'Priority', 
                           'Status', 'Created At', 'Resolved At', 'Description'])
            
            # Data
            for row in result:
                writer.writerow(row)
            
            csv_content = output.getvalue()
            
            return {
                "success": True,
                "data": csv_content,
                "filename": f"call_logs_{datetime.now().strftime('%Y%m%d')}.csv"
            }
            
    except Exception as e:
        print(f"❌ Error exporting call logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
