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


def vapi_speak(text: str):
    return [{"type": "output_text", "text": text}]


def empty_openai_response(text: str):
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
                    "content": vapi_speak(text)
                },
                "finish_reason": "stop"
            }
        ]
    }


@router.post("/chat/completions")
async def chat_completion(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    if not messages:
        return empty_openai_response("Hello, how can I help you today?")

    user_query = messages[-1].get("content", "").strip()
    if not user_query:
        return empty_openai_response("Hello, how can I help you today?")

    user_confirmed = any(word in user_query.lower() for word in CONFIRM_WORDS)

    context = await rag_service.get_context(user_query)
    ai_message = await get_ai_response(
        user_query=user_query,
        context=context,
        user_confirmed=user_confirmed
    )

    spoken_text = ai_message.get("content", "").strip()
    if not spoken_text:
        spoken_text = "Please tell me your name and describe your complaint."

    tool_calls = ai_message.get("tool_calls", [])

    for tool in tool_calls:
        if tool["name"] == "register_grievance":
            args = json.loads(tool["arguments"])

            ticket_id = f"DEL-{uuid.uuid4().hex[:6].upper()}"

            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO grievances (ticket_id, citizen_name, description, status)
                        VALUES (:ticket_id, :name, :issue, :status)
                    """),
                    {
                        "ticket_id": ticket_id,
                        "name": args["name"],
                        "issue": args["issue"],
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

            spoken_text = (
                f"Your complaint has been registered successfully. "
                f"Your ticket number is {ticket_id}."
            )

    print("===== FINAL ASSISTANT RESPONSE =====")
    print(spoken_text)
    print("===================================")

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
