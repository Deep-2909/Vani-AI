import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.rag import RAGService
from app.services.llm import get_ai_response

CALL_STATE = {}
router = APIRouter()
rag_service = RAGService()

@router.websocket("/llm-websocket/call_{call_id}")
async def retell_llm_ws(websocket: WebSocket, call_id: str):
    await websocket.accept()
    print(f"✅ Retell connected | call_id={call_id}")

    # ✅ Initialize call state
    CALL_STATE[call_id] = {
        "issue": None,
        "name": None,
        "confirmed": False,
        "registered": False
    }

    try:
        # Initial greeting
        await websocket.send_json({
            "response_id": 0,
            "content": "Namaste, I am Vani from the Delhi Government. How can I help you?",
            "content_complete": True,
            "end_call": False
        })

        while True:
            data = await websocket.receive_json()

            # 🔹 Retell heartbeat
            if data.get("interaction_type") == "ping_pong":
                await websocket.send_json({
                    "interaction_type": "ping_pong",
                    "timestamp": data.get("timestamp")
                })
                continue

            # 🔹 Retell: user finished speaking
            if data.get("interaction_type") == "response_required":
                response_id = data["response_id"]
                transcript = data.get("transcript", [])

                # 🔹 Log full transcript
                print("\n📜 TRANSCRIPT:")
                for t in transcript:
                    print(f"{t['role'].upper()}: {t['content']}")

                # 🔹 Get latest user message
                user_text = ""
                for t in reversed(transcript):
                    if t["role"] == "user":
                        user_text = t["content"].strip().lower()
                        break

                print(f"🗣 USER SAID (latest): {user_text}")

                state = CALL_STATE[call_id]

                # -----------------------------
                # 🧠 STATE-DRIVEN CONVERSATION
                # -----------------------------

                if not state["issue"]:
                    state["issue"] = user_text
                    reply = "Thank you. Could you please describe the issue in a bit more detail?"

                elif not state["name"]:
                    if "my name is" in user_text or "i am" in user_text:
                        state["name"] = user_text
                        reply = "Thank you. Would you like me to register this complaint now?"
                    else:
                        reply = "Please tell me your name for the complaint registration."

                elif not state["confirmed"]:
                    if any(word in user_text for word in ["yes", "yeah", "confirm", "go ahead", "sure"]):
                        state["confirmed"] = True
                        reply = "Understood. I am registering your complaint now."
                    else:
                        reply = "Please confirm if you would like me to register the complaint."

                elif not state["registered"]:
                    # 🔥 This is where DB / tool logic can be called
                    state["registered"] = True
                    reply = "Your complaint has been registered successfully. Thank you for calling."

                else:
                    reply = "Your complaint is already registered. Is there anything else I can help you with?"

                await websocket.send_json({
                    "response_id": response_id,
                    "content": reply,
                    "content_complete": True,
                    "end_call": state["registered"]
                })

                print(f"🤖 AI → {reply}")

    except WebSocketDisconnect:
        print(f"❌ Retell disconnected | call_id={call_id}")
        CALL_STATE.pop(call_id, None)

    except Exception as e:
        print(f"🚨 ERROR | call_id={call_id} | {e}")
        CALL_STATE.pop(call_id, None)
