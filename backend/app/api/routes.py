from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text
from app.db import engine
from app.ws import manager


router = APIRouter()

class GrievanceRequest(BaseModel):
    citizen_name: str
    description: str


@router.post("/chat/completions")
async def chat_completion(data: GrievanceRequest):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO grievances (ticket_id, citizen_name, status)
                VALUES (:ticket_id, :citizen_name, :status)
                RETURNING id
            """),
            {
                "ticket_id": f"TICKET-{data.citizen_name[:3].upper()}",
                "citizen_name": data.citizen_name,
                "status": "OPEN"
            }
        )
        grievance_id = result.fetchone()[0]

    await manager.broadcast({
        "event": "NEW_GRIEVANCE",
        "grievance_id": grievance_id,
        "citizen_name": data.citizen_name
    })

    return {
        "message": "Grievance registered successfully",
        "grievance_id": grievance_id,
        "citizen_name": data.citizen_name
    }
