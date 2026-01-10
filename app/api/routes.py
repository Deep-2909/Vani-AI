import json
import uuid
import time
from fastapi import APIRouter, Request
from sqlalchemy import text
from app.db import engine
from app.ws import manager
from app.services.rag import RAGService
from app.services.llm import get_ai_response

router = APIRouter()
rag_service = RAGService()

CONFIRM_WORDS = ["yes", "yeah", "yep", "please do", "go ahead", "confirm", "sure"]

@router.post("/chat/completions")
async def chat_completion(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    print("\n🗣️ USER SAID:")
    for m in messages:
        if m['role'] == 'user':
            print(f"USER: {m['content']}")

    if not messages:
        return openai_response("Namaste, I am Vani. How can I help you today?")

    user_query = messages[-1].get("content", "").strip()

    # RAG lookup
    context = await rag_service.get_context(user_query)
    user_confirmed = any(word in user_query.lower() for word in CONFIRM_WORDS)

    # Get AI response
    ai_message = await get_ai_response(
        messages=messages,
        context=context,
        user_confirmed=user_confirmed
    )

    spoken_text = ai_message.get("content", "").strip()
    tool_calls = ai_message.get("tool_calls", [])

    # Handle Tool Calls (Grievance Registration)
    for tool in tool_calls:
        if tool["name"] == "register_grievance":
            try:
                args = json.loads(tool["arguments"])
                ticket_id = f"DEL-{uuid.uuid4().hex[:6].upper()}"

                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO grievances 
                            (ticket_id, citizen_name, description, department, status)
                            VALUES (:ticket_id, :name, :issue, :dept, :status)
                        """),
                        {
                            "ticket_id": ticket_id,
                            "name": args["name"],
                            "issue": args["issue"],
                            "dept": args["department"],
                            "status": "OPEN"
                        }
                    )

                await manager.broadcast({
                    "event": "NEW_GRIEVANCE",
                    "data": {
                        "ticket_id": ticket_id,
                        "citizen_name": args["name"],
                        "issue": args["issue"],
                        "department": args["department"]
                    }
                })

                spoken_text = f"Thank you. Your complaint is registered with ticket number {ticket_id}."
            except Exception as e:
                print(f"❌ DB ERROR: {e}")
                spoken_text = "I'm having trouble saving your complaint right now, but I have noted the details."

    print(f"\n🤖 ASSISTANT SAID: {spoken_text}")

    return openai_response(spoken_text)

def openai_response(text: str):
    """Returns a full OpenAI-compatible JSON to trigger Vapi TTS."""
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
                    "content": text
                },
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }