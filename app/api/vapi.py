from fastapi import APIRouter, Request
import requests

router = APIRouter()

LLM_ENDPOINT = "http://localhost:8000/llm/respond"  # your logic layer

@router.post("/vapi/callback")
async def vapi_callback(request: Request):
    payload = await request.json()

    print("\n================ VAPI PAYLOAD ================\n")
    print(payload)
    print("\n==============================================\n")

    # 🛡️ 1. Ignore non-user events safely
    if "message" not in payload:
        return _vapi_speak("Hello, how can I assist you today?")

    user_text = payload["message"].get("content", "").strip()

    if not user_text:
        return _vapi_speak("I could not hear you clearly. Please repeat.")

    # 🧠 2. Send text to your LLM (NO keyword logic here)
    try:
        llm_response = requests.post(
            LLM_ENDPOINT,
            json={
                "text": user_text,
                "call_id": payload.get("call", {}).get("id")
            },
            timeout=10
        ).json()

        assistant_text = llm_response.get(
            "response",
            "Could you please rephrase your request?"
        )

    except Exception as e:
        print("LLM ERROR:", e)
        assistant_text = "I am facing a technical issue. Please try again."

    # 🔊 3. Send back to VAPI in correct format
    return _vapi_speak(assistant_text)


def _vapi_speak(text: str):
    """Always returns valid VAPI speech response"""
    return {
        "response": {
            "output": [
                {
                    "type": "output_text",
                    "text": text
                }
            ]
        }
    }
