import json
import uuid
from datetime import datetime
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
CONFIRM_WORDS = ["yes", "yeah", "yep", "please", "go ahead", "confirm", "sure", "okay", "ok", "proceed"]


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

    # Initialize conversation history
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
        
        CONVERSATION_HISTORY[call_id].append({
            "role": "assistant",
            "content": greeting
        })

        while True:
            data = await websocket.receive_json()

            # Handle heartbeat
            if data.get("interaction_type") == "ping_pong":
                await websocket.send_json({
                    "interaction_type": "ping_pong",
                    "timestamp": data.get("timestamp")
                })
                continue

            # Handle user speech
            if data.get("interaction_type") == "response_required":
                response_id = data["response_id"]
                transcript = data.get("transcript", [])

                user_text = extract_latest_user_message(transcript)
                
                if not user_text:
                    continue

                print(f"\n🗣️ USER SAID: {user_text}")

                # Add to history
                CONVERSATION_HISTORY[call_id].append({
                    "role": "user",
                    "content": user_text
                })

                # Get RAG context
                context = await rag_service.get_context(user_text)
                
                # Detect confirmation
                user_confirmed = detect_confirmation(user_text)

                # Get AI response with multi-intent detection
                ai_response = await get_ai_response(
                    messages=CONVERSATION_HISTORY[call_id],
                    context=context,
                    user_confirmed=user_confirmed
                )

                spoken_text = ai_response.get("content", "").strip()
                tool_calls = ai_response.get("tool_calls", [])

                # ===================================================================
                # HANDLE MULTIPLE TOOL CALLS
                # ===================================================================

                for tool in tool_calls:
                    tool_name = tool["name"]
                    
                    try:
                        args = json.loads(tool["arguments"])
                        
                        # ---------------------------------------------------------------
                        # TOOL 1: REGISTER GRIEVANCE
                        # ---------------------------------------------------------------
                        if tool_name == "register_grievance":
                            ticket_id = f"DEL-{uuid.uuid4().hex[:6].upper()}"

                            print(f"\n📝 REGISTERING GRIEVANCE:")
                            print(f"   Ticket ID: {ticket_id}")
                            print(f"   Name: {args.get('name')}")
                            print(f"   Issue: {args.get('issue')}")
                            print(f"   Location: {args.get('location')}")
                            print(f"   Category: {args.get('category')}")
                            print(f"   Priority: {args.get('priority')}")
                            print(f"   Department: {args.get('department')}")

                            with engine.begin() as conn:
                                conn.execute(
                                    text("""
                                        INSERT INTO grievances 
                                        (ticket_id, citizen_name, contact, description, location, 
                                         department, category, priority, status, call_id)
                                        VALUES (:ticket_id, :name, :contact, :issue, :location,
                                                :dept, :category, :priority, :status, :call_id)
                                    """),
                                    {
                                        "ticket_id": ticket_id,
                                        "name": args.get("name", "Unknown"),
                                        "contact": args.get("contact", ""),
                                        "issue": args.get("issue", ""),
                                        "location": args.get("location", ""),
                                        "dept": args.get("department", "General/PGC"),
                                        "category": args.get("category", "Other"),
                                        "priority": args.get("priority", "Medium"),
                                        "status": "OPEN",
                                        "call_id": call_id
                                    }
                                )

                            # Broadcast to dashboard
                            await manager.broadcast({
                                "event": "NEW_GRIEVANCE",
                                "data": {
                                    "ticket_id": ticket_id,
                                    "citizen_name": args.get("name"),
                                    "issue": args.get("issue"),
                                    "location": args.get("location"),
                                    "category": args.get("category"),
                                    "priority": args.get("priority"),
                                    "department": args.get("department"),
                                    "call_id": call_id
                                }
                            })

                            spoken_text = (
                                f"Your complaint has been registered successfully. "
                                f"Your ticket number is {ticket_id}. "
                                f"This has been marked as {args.get('priority', 'Medium')} priority. "
                                f"You will receive SMS updates on {args.get('contact')}. "
                                f"Is there anything else I can help you with?"
                            )
                            
                            print(f"✅ Complaint registered: {ticket_id}")

                        # ---------------------------------------------------------------
                        # TOOL 2: CHECK STATUS
                        # ---------------------------------------------------------------
                        elif tool_name == "check_complaint_status":
                            ticket_id = args.get("ticket_id", "").upper()
                            
                            print(f"\n🔍 CHECKING STATUS: {ticket_id}")

                            # Log the status check
                            with engine.begin() as conn:
                                conn.execute(
                                    text("""
                                        INSERT INTO status_checks 
                                        (ticket_id, phone_number, call_id)
                                        VALUES (:ticket_id, :phone, :call_id)
                                    """),
                                    {
                                        "ticket_id": ticket_id,
                                        "phone": args.get("phone_number", ""),
                                        "call_id": call_id
                                    }
                                )
                                
                                # Fetch complaint details
                                result = conn.execute(
                                    text("""
                                        SELECT ticket_id, status, description, department, 
                                               category, priority, created_at, resolved_at
                                        FROM grievances 
                                        WHERE ticket_id = :ticket_id
                                    """),
                                    {"ticket_id": ticket_id}
                                )
                                
                                complaint = result.fetchone()

                            if complaint:
                                status = complaint[1]
                                dept = complaint[3]
                                priority = complaint[5]
                                
                                status_messages = {
                                    "OPEN": "is currently open and being reviewed by",
                                    "IN_PROGRESS": "is in progress and being handled by",
                                    "RESOLVED": "has been resolved by",
                                    "CLOSED": "has been closed by",
                                    "ESCALATED": "has been escalated to higher authorities in"
                                }
                                
                                spoken_text = (
                                    f"Your complaint with ticket number {ticket_id} "
                                    f"{status_messages.get(status, 'is being processed by')} "
                                    f"{dept}. "
                                    f"This is a {priority} priority issue. "
                                    f"Is there anything else I can help you with?"
                                )
                            else:
                                spoken_text = (
                                    f"I could not find a complaint with ticket number {ticket_id}. "
                                    f"Please check the ticket number and try again."
                                )
                            
                            print(f"✅ Status checked: {ticket_id}")

                        # ---------------------------------------------------------------
                        # TOOL 3: ESCALATE COMPLAINT
                        # ---------------------------------------------------------------
                        elif tool_name == "escalate_complaint":
                            ticket_id = args.get("ticket_id", "").upper()
                            reason = args.get("reason", "")
                            
                            print(f"\n⬆️ ESCALATING: {ticket_id}")

                            with engine.begin() as conn:
                                # Log escalation
                                conn.execute(
                                    text("""
                                        INSERT INTO escalations 
                                        (ticket_id, reason, escalated_by, call_id)
                                        VALUES (:ticket_id, :reason, :phone, :call_id)
                                    """),
                                    {
                                        "ticket_id": ticket_id,
                                        "reason": reason,
                                        "phone": args.get("phone_number", ""),
                                        "call_id": call_id
                                    }
                                )
                                
                                # Update complaint status
                                conn.execute(
                                    text("""
                                        UPDATE grievances 
                                        SET status = 'ESCALATED',
                                            escalated = escalated + 1,
                                            escalation_reason = :reason,
                                            updated_at = NOW()
                                        WHERE ticket_id = :ticket_id
                                    """),
                                    {"ticket_id": ticket_id, "reason": reason}
                                )

                            spoken_text = (
                                f"Your complaint {ticket_id} has been escalated to senior authorities. "
                                f"You will receive a call from a senior officer within 24 hours. "
                                f"Is there anything else I can help you with?"
                            )
                            
                            print(f"✅ Escalated: {ticket_id}")

                        # ---------------------------------------------------------------
                        # TOOL 4: GENERAL INFO
                        # ---------------------------------------------------------------
                        elif tool_name == "provide_general_info":
                            query_type = args.get("query_type", "")
                            
                            print(f"\n📖 PROVIDING INFO: {query_type}")
                            
                            # Spoken text should already be generated by LLM based on RAG context
                            if not spoken_text:
                                spoken_text = (
                                    "Based on the available information, I can help you with that. "
                                    "Is there anything specific you'd like to know?"
                                )

                        # ---------------------------------------------------------------
                        # TOOL 5: RECORD FEEDBACK
                        # ---------------------------------------------------------------
                        elif tool_name == "record_feedback":
                            rating = args.get("rating", 3)
                            feedback_text = args.get("feedback_text", "")
                            
                            print(f"\n⭐ RECORDING FEEDBACK: {rating}/5")

                            with engine.begin() as conn:
                                conn.execute(
                                    text("""
                                        INSERT INTO feedback 
                                        (ticket_id, rating, feedback_text, phone_number, call_id)
                                        VALUES (:ticket_id, :rating, :feedback, :phone, :call_id)
                                    """),
                                    {
                                        "ticket_id": args.get("ticket_id", None),
                                        "rating": rating,
                                        "feedback": feedback_text,
                                        "phone": args.get("phone_number", ""),
                                        "call_id": call_id
                                    }
                                )

                            spoken_text = (
                                f"Thank you for your feedback. "
                                f"Your {rating}-star rating has been recorded. "
                                f"We appreciate your input in helping us improve our services."
                            )
                            
                            print(f"✅ Feedback recorded: {rating}/5")

                        # ---------------------------------------------------------------
                        # TOOL 6: EMERGENCY
                        # ---------------------------------------------------------------
                        elif tool_name == "emergency_assistance":
                            emergency_type = args.get("emergency_type", "")
                            location = args.get("location", "")
                            
                            print(f"\n🚨 EMERGENCY: {emergency_type} at {location}")

                            with engine.begin() as conn:
                                conn.execute(
                                    text("""
                                        INSERT INTO emergencies 
                                        (emergency_type, location, phone_number, description, call_id)
                                        VALUES (:type, :location, :phone, :description, :call_id)
                                    """),
                                    {
                                        "type": emergency_type,
                                        "location": location,
                                        "phone": args.get("phone_number", ""),
                                        "description": args.get("description", ""),
                                        "call_id": call_id
                                    }
                                )

                            # Broadcast emergency alert
                            await manager.broadcast({
                                "event": "EMERGENCY_ALERT",
                                "data": {
                                    "type": emergency_type,
                                    "location": location,
                                    "phone": args.get("phone_number"),
                                    "description": args.get("description"),
                                    "call_id": call_id
                                }
                            })

                            spoken_text = (
                                f"I have immediately notified emergency services about the {emergency_type} "
                                f"at {location}. Help is on the way. Please stay on the line."
                            )
                            
                            print(f"🚨 Emergency logged and escalated!")

                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parsing error: {e}")
                        spoken_text = "I apologize, I had trouble processing that. Could you please repeat?"

                    except Exception as e:
                        print(f"❌ Tool execution error: {e}")
                        import traceback
                        traceback.print_exc()
                        spoken_text = (
                            "I apologize, I'm having technical difficulties. "
                            "Please try again or contact our helpline at 1800-XXX-XXXX."
                        )

                # Ensure we have something to say
                if not spoken_text:
                    spoken_text = "I'm sorry, could you please repeat that?"

                print(f"🤖 ASSISTANT SAID: {spoken_text}")

                # Send response
                await websocket.send_json({
                    "response_id": response_id,
                    "content": spoken_text,
                    "content_complete": True,
                    "end_call": False
                })

                # Add to history
                CONVERSATION_HISTORY[call_id].append({
                    "role": "assistant",
                    "content": spoken_text
                })

                # Limit history
                if len(CONVERSATION_HISTORY[call_id]) > 20:
                    CONVERSATION_HISTORY[call_id] = CONVERSATION_HISTORY[call_id][-18:]

    except WebSocketDisconnect:
        print(f"❌ Retell disconnected | call_id={call_id}")
        
    except Exception as e:
        print(f"🚨 ERROR | call_id={call_id} | {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        CONVERSATION_HISTORY.pop(call_id, None)
        print(f"🧹 Cleaned up call state for {call_id}")
