"""
Retell Webhook Handler
Receives webhooks from Retell AI for call events
"""
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import text
from app.db import engine
import json

router = APIRouter()


@router.post("/api/retell/webhook")
async def retell_webhook(request: Request):
    """
    Handle webhooks from Retell AI
    Supported events:
    - call_started: When call begins
    - call_ended: When call ends (extracts duration)
    - call_analyzed: When post-call analysis completes
    """
    try:
        payload = await request.json()
        event = payload.get("event")
        call_data = payload.get("call", {})

        print(f"\n{'='*80}")
        print(f"📥 RETELL WEBHOOK RECEIVED: {event}")
        print(f"{'='*80}")

        if event == "call_ended":
            call_id = call_data.get("call_id")
            start_timestamp = call_data.get("start_timestamp")  # milliseconds
            end_timestamp = call_data.get("end_timestamp")  # milliseconds
            duration_ms = call_data.get("duration_ms")

            print(f"📞 Call ID (from webhook): {call_id}")

            # Strip 'call_' prefix if present to match database format
            call_id_stripped = call_id.replace("call_", "") if call_id and call_id.startswith("call_") else call_id
            print(f"📞 Call ID (stripped): {call_id_stripped}")

            print(f"⏱️  Start: {start_timestamp}")
            print(f"⏱️  End: {end_timestamp}")
            print(f"⏱️  Duration (ms): {duration_ms}")

            # Calculate duration in seconds
            if duration_ms is not None:
                duration_seconds = duration_ms // 1000
            elif start_timestamp and end_timestamp:
                duration_seconds = (end_timestamp - start_timestamp) // 1000
            else:
                duration_seconds = 0

            print(f"✅ Calculated duration: {duration_seconds} seconds ({duration_seconds // 60}m {duration_seconds % 60}s)")

            # Update the grievance record with actual call duration
            with engine.begin() as conn:
                result = conn.execute(
                    text("""
                        UPDATE grievances
                        SET call_duration = :duration
                        WHERE retell_call_id = :call_id
                        RETURNING ticket_id
                    """),
                    {
                        "duration": duration_seconds,
                        "call_id": call_id_stripped
                    }
                )

                updated_row = result.fetchone()
                if updated_row:
                    print(f"✅ Updated grievance {updated_row[0]} with duration: {duration_seconds}s")
                else:
                    print(f"⚠️  No grievance found with retell_call_id: {call_id_stripped}")

            print(f"{'='*80}\n")

            return {
                "success": True,
                "message": "Call duration updated",
                "call_id": call_id_stripped,
                "duration_seconds": duration_seconds
            }

        elif event == "call_started":
            call_id = call_data.get("call_id")
            print(f"📞 Call started: {call_id}")
            print(f"{'='*80}\n")

            return {
                "success": True,
                "message": "Call start acknowledged",
                "call_id": call_id
            }

        elif event == "call_analyzed":
            call_id = call_data.get("call_id")
            print(f"🔍 Call analyzed: {call_id}")
            # Could store analysis data here if needed
            print(f"{'='*80}\n")

            return {
                "success": True,
                "message": "Call analysis acknowledged",
                "call_id": call_id
            }

        else:
            print(f"⚠️  Unknown event type: {event}")
            print(f"{'='*80}\n")

            return {
                "success": True,
                "message": f"Event {event} acknowledged but not processed"
            }

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/retell/webhook/test")
async def test_webhook():
    """
    Test endpoint to verify webhook is accessible
    """
    return {
        "status": "active",
        "message": "Retell webhook endpoint is ready to receive events",
        "supported_events": ["call_started", "call_ended", "call_analyzed"]
    }
