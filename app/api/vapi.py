from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/vapi/callback")
async def vapi_callback(request: Request):
    """
    In Custom LLM mode, this endpoint receives Status Updates 
    (call started, call ended, errors) but NOT chat completions.
    """
    payload = await request.json()
    
    message_type = payload.get("message", {}).get("type")
    
    print(f"\n[VAPI EVENT]: {message_type}")
    
    if message_type == "status-update":
        print(f"Call Status: {payload.get('message', {}).get('status')}")
    
    if "error" in str(payload).lower():
        print(f"🚨 VAPI ERROR DETECTED: {payload}")

    return {"status": "ok"}