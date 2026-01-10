import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import text
from app.services.rag import RAGService
from app.services.llm import get_ai_response
from app.db import engine
from app.ws import manager

router = APIRouter()
rag_service = RAGService()

# Store conversation history per call
CONVERSATION_HISTORY = {}

# Confirmation keywords
CONFIRM_WORDS = ["yes", "yeah", "yep", "please", "go ahead", "confirm", "sure", "okay", "ok"]


def extract_latest_user_message(transcript: list) -> str:
    """Extract the most recent user message from Retell transcript."""
    for item in reversed(transcript):
        if item.get("role") == "user":
            return item.get("content", "").strip()
    return ""


def detect_confirmation(text: str) -> bool:
    """Check if user is confirming."""
    text_lower = text.lower()
    return any(word in text_lower for word in CONFIRM_WORDS)


@router.websocket("/llm-websocket/call_{call_id}")
async def retell_llm_ws(websocket: WebSocket, call_id: str):
    await websocket.accept()
    print(f"✅ Retell connected | call_id={call_id}")

    # Initialize conversation history for this call
    CONVERSATION_HISTORY[call_id] = []

    try:
        # Send initial greeting
        greeting = "Namaste, I am Vani from the Delhi Government. How can I help you today?"
        
        await websocket.send_json({
            "response_id": 0,
            "content": greeting,
            "content_complete": True,
            "end_call": False
        })
        
        # Add to history
        CONVERSATION_HISTORY[call_id].append({
            "role": "assistant",
            "content": greeting
        })

        while True:
            data = await websocket.receive_json()

            # Handle Retell heartbeat (ping-pong)
            if data.get("interaction_type") == "ping_pong":
                await websocket.send_json({
                    "interaction_type": "ping_pong",
                    "timestamp": data.get("timestamp")
                })
                continue

            # Handle user speech completion
            if data.get("interaction_type") == "response_required":
                response_id = data["response_id"]
                transcript = data.get("transcript", [])

                # Extract latest user message
                user_text = extract_latest_user_message(transcript)
                
                if not user_text:
                    print("⚠️ No user text found in transcript")
                    continue

                print(f"\n🗣️ USER SAID: {user_text}")

                # Add user message to history
                CONVERSATION_HISTORY[call_id].append({
                    "role": "user",
                    "content": user_text
                })

                # Get RAG context
                context = await rag_service.get_context(user_text)
                
                # Detect confirmation
                user_confirmed = detect_confirmation(user_text)

                # Get AI response using your existing LLM service
                ai_response = await get_ai_response(
                    messages=CONVERSATION_HISTORY[call_id],
                    context=context,
                    user_confirmed=user_confirmed
                )

                spoken_text = ai_response.get("content", "").strip()
                tool_calls = ai_response.get("tool_calls", [])

                # Handle tool calls (complaint registration)
                complaint_registered = False
                ticket_id = None

                for tool in tool_calls:
                    if tool["name"] == "register_grievance":
                        try:
                            args = json.loads(tool["arguments"])
                            ticket_id = f"DEL-{uuid.uuid4().hex[:6].upper()}"

                            print(f"\n📝 REGISTERING GRIEVANCE:")
                            print(f"   Ticket ID: {ticket_id}")
                            print(f"   Name: {args.get('name')}")
                            print(f"   Issue: {args.get('issue')}")
                            print(f"   Department: {args.get('department')}")

                            # Insert into database
                            with engine.begin() as conn:
                                conn.execute(
                                    text("""
                                        INSERT INTO grievances 
                                        (ticket_id, citizen_name, description, department, status, call_id)
                                        VALUES (:ticket_id, :name, :issue, :dept, :status, :call_id)
                                    """),
                                    {
                                        "ticket_id": ticket_id,
                                        "name": args.get("name", "Unknown"),
                                        "issue": args.get("issue", ""),
                                        "dept": args.get("department", "General/PGC"),
                                        "status": "OPEN",
                                        "call_id": call_id
                                    }
                                )

                            # Broadcast to WebSocket clients (dashboard)
                            await manager.broadcast({
                                "event": "NEW_GRIEVANCE",
                                "data": {
                                    "ticket_id": ticket_id,
                                    "citizen_name": args.get("name"),
                                    "issue": args.get("issue"),
                                    "department": args.get("department"),
                                    "call_id": call_id
                                }
                            })

                            # Update spoken text with ticket ID
                            spoken_text = (
                                f"Thank you. Your complaint has been registered successfully. "
                                f"Your ticket number is {ticket_id}. "
                                f"You will receive updates on your registered mobile number. "
                                f"Is there anything else I can help you with?"
                            )
                            
                            complaint_registered = True
                            print(f"✅ Complaint registered: {ticket_id}")

                        except Exception as e:
                            print(f"❌ DATABASE ERROR: {e}")
                            spoken_text = (
                                "I apologize, but I'm having trouble registering your complaint right now. "
                                "Please try calling again or visit the nearest citizen service center."
                            )

                # Ensure we have something to say
                if not spoken_text:
                    spoken_text = "I'm sorry, could you please repeat that?"

                print(f"🤖 ASSISTANT SAID: {spoken_text}")

                # Send response to Retell
                await websocket.send_json({
                    "response_id": response_id,
                    "content": spoken_text,
                    "content_complete": True,
                    "end_call": False  # Don't auto-end call
                })

                # Add assistant response to history
                CONVERSATION_HISTORY[call_id].append({
                    "role": "assistant",
                    "content": spoken_text
                })

                # Limit conversation history to last 20 messages to avoid token limits
                if len(CONVERSATION_HISTORY[call_id]) > 20:
                    # Keep system message and last 18 messages
                    CONVERSATION_HISTORY[call_id] = CONVERSATION_HISTORY[call_id][-18:]

    except WebSocketDisconnect:
        print(f"❌ Retell disconnected | call_id={call_id}")
        
    except Exception as e:
        print(f"🚨 ERROR | call_id={call_id} | {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup conversation history
        CONVERSATION_HISTORY.pop(call_id, None)
        print(f"🧹 Cleaned up call state for {call_id}")