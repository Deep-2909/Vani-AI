from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/vapi/callback")
async def vapi_callback(request: Request):
    payload = await request.json()
    print("VAPI PAYLOAD:", payload)
    return {"status": "received"}
