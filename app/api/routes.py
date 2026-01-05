import json
import uuid
import time
from fastapi import APIRouter, Request
from sqlalchemy import text
from app.db import engine
from app.ws import manager

from app.services.rag import RAGService
from app.services.llm import get_ai_response

def vapi_speak(text: str):
    return [
        {
            "type": "output_text",
            "text": text
        }
    ]
router = APIRouter()
rag_service = RAGService()


@router.post("/chat/completions")
async def chat_completion(request: Request):
    body = await request.json()

    # SAFETY: ensure messages exist
    messages = body.get("messages", [])
    if not messages:
        return _empty_vapi_response()

    user_query = messages[-1].get("content", "").strip()
    if not user_query:
        return _empty_vapi_response()

    # 1️⃣ RAG + LLM
    context = await rag_service.get_context(user_query)
    ai_message = await get_ai_response(user_query, context)

    # 2️⃣ Default assistant text
    spoken_text = ai_message["content"] or "I have processed your request."

    # 3️⃣ TOOL EXECUTION (SIDE EFFECTS ONLY)
    if ai_message.tool_calls:
        for tool in ai_message.tool_calls:
            if tool.function.name == "register_grievance":
                try:
                    args = json.loads(tool.function.arguments)
                except Exception:
                    continue

                ticket_id = f"DEL-{uuid.uuid4().hex[:6].upper()}"

                # DB insert
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO grievances (ticket_id, citizen_name, description, status)
                            VALUES (:ticket_id, :name, :issue, :status)
                        """),
                        {
                            "ticket_id": ticket_id,
                            "name": args.get("name"),
                            "issue": args.get("issue"),
                            "status": "OPEN"
                        }
                    )

                # Broadcast to dashboard
                await manager.broadcast({
                    "event": "NEW_GRIEVANCE",
                    "data": {
                        "ticket_id": ticket_id,
                        "citizen_name": args.get("name"),
                        "issue": args.get("issue"),
                        "department": args.get("department")
                    }
                })

                # 🔴 CRITICAL FIX: override spoken text for VAPI
                spoken_text = (
                    f"Your complaint has been registered successfully. "
                    f"Your ticket number is {ticket_id}."
                )

    # 4️⃣ RETURN FINAL RESPONSE TO VAPI (NO tool_calls)
    return {
    "id": f"chatcmpl-{uuid.uuid4()}",
    "object": "chat.completion",
    "created": int(time.time()),
    "model": "gpt-4o",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": vapi_speak(spoken_text)
            },
            "finish_reason": "stop"
        }
    ]
}



# -----------------------------
# Helper fallback response
# -----------------------------
def _empty_vapi_response():
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": vapi_speak("Hello, how can I help you today?")
                },
                "finish_reason": "stop"
            }
        ]
    }
