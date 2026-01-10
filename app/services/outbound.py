"""
Outbound Call Service
Initiates government-initiated calls using Retell AI for:
- Scheme notifications
- Area alerts
- Follow-ups
"""
import os
import httpx
from typing import List, Dict
from datetime import datetime
from sqlalchemy import text
from app.db import engine

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
RETELL_API_URL = "https://api.retellai.com/v1"

# ===================================================================
# MESSAGE TEMPLATES (Multilingual)
# ===================================================================

SCHEME_TEMPLATES = {
    "hindi": """
Namaste {name},
Main Vani bol rahi hoon Delhi Sarkar ki taraf se.

Aapko ek important scheme ke baare mein batana chahti hoon:
{scheme_name}

{scheme_description}

Agar aap eligible hain, toh aap apply kar sakte hain {application_url} par.

Kya aapko is scheme ke baare mein aur jaankari chahiye?
""",
    "punjabi": """
Sat Sri Akal {name},
Main Vani haan Delhi Sarkar di taraf to.

Tuhanu ek important scheme bare dassna chahundi haan:
{scheme_name}

{scheme_description}

Je tussi eligible ho, taan tussi apply kar sakde ho {application_url} te.

Ki tuhanu is scheme bare hor jaankari chahiye?
""",
    "english": """
Hello {name},
This is Vani calling from Delhi Government.

I want to inform you about an important government scheme:
{scheme_name}

{scheme_description}

If you are eligible, you can apply at {application_url}.

Would you like more information about this scheme?
"""
}

ALERT_TEMPLATES = {
    "hindi": """
Namaste,
Main Vani bol rahi hoon Delhi Sarkar ki taraf se.

Aapke area {area_name} mein ek important alert hai:
{alert_message}

Kripya is information ko apne area ke logon ke saath share karein.

Dhanyavaad.
""",
    "punjabi": """
Sat Sri Akal,
Main Vani haan Delhi Sarkar di taraf to.

Tuhade area {area_name} vich ek important alert hai:
{alert_message}

Meharbani karke eh information apne area de loka naal share karo.

Shukriya.
""",
    "english": """
Hello,
This is Vani from Delhi Government.

There is an important alert for your area {area_name}:
{alert_message}

Please share this information with people in your area.

Thank you.
"""
}

FOLLOW_UP_TEMPLATES = {
    "hindi": """
Namaste {name},
Main Vani bol rahi hoon Delhi Sarkar ki taraf se.

Aapki complaint {ticket_id} ke baare mein update dena chahti hoon.

{update_message}

Kya aap is solution se satisfied hain?
""",
    "punjabi": """
Sat Sri Akal {name},
Main Vani haan Delhi Sarkar di taraf to.

Tuhadi complaint {ticket_id} bare update dena chahundi haan.

{update_message}

Ki tussi is solution naal satisfied ho?
""",
    "english": """
Hello {name},
This is Vani from Delhi Government.

I'm calling to update you about your complaint {ticket_id}.

{update_message}

Are you satisfied with this resolution?
"""
}


# ===================================================================
# RETELL API INTEGRATION
# ===================================================================

async def create_retell_call(
    phone_number: str,
    message: str,
    language: str = "hindi"
) -> Dict:
    """
    Create an outbound call using Retell AI API.
    """
    if not RETELL_API_KEY:
        print("⚠️ RETELL_API_KEY not configured")
        return {"success": False, "error": "API key missing"}
    
    try:
        headers = {
            "Authorization": f"Bearer {RETELL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Prepare call data
        call_data = {
            "from_number": os.getenv("RETELL_FROM_NUMBER", "+911234567890"),
            "to_number": phone_number,
            "override_agent_id": os.getenv("RETELL_AGENT_ID"),
            "metadata": {
                "call_type": "outbound_government",
                "language": language,
                "message": message
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RETELL_API_URL}/create-phone-call",
                headers=headers,
                json=call_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "call_id": result.get("call_id"),
                    "status": result.get("status")
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
                
    except Exception as e:
        print(f"❌ Error creating Retell call: {e}")
        return {"success": False, "error": str(e)}


# ===================================================================
# OUTBOUND CALL FUNCTIONS
# ===================================================================

async def send_scheme_notification(
    scheme_code: str,
    phone_numbers: List[str],
    language: str = "hindi"
):
    """
    Send scheme notifications to a list of phone numbers.
    """
    try:
        with engine.connect() as conn:
            # Get scheme details
            result = conn.execute(
                text("""
                    SELECT scheme_name, short_description, application_url, 
                           notification_message
                    FROM government_schemes 
                    WHERE scheme_code = :code AND is_active = TRUE
                """),
                {"code": scheme_code}
            )
            
            scheme = result.fetchone()
            if not scheme:
                return {"success": False, "error": "Scheme not found"}
            
            # Generate message
            template = SCHEME_TEMPLATES.get(language, SCHEME_TEMPLATES["english"])
            message = template.format(
                name="Citizen",  # Can be personalized if name is available
                scheme_name=scheme[0],
                scheme_description=scheme[1],
                application_url=scheme[2] or "Delhi Government website"
            )
            
            # Make calls
            results = []
            for phone in phone_numbers:
                call_result = await create_retell_call(phone, message, language)
                
                # Log in database
                with engine.begin() as conn_log:
                    conn_log.execute(
                        text("""
                            INSERT INTO outbound_calls
                            (call_id, phone_number, call_type, message_content,
                             scheme_name, status, initiated_at, language)
                            VALUES
                            (:call_id, :phone, 'scheme_notification', :message,
                             :scheme, :status, NOW(), :language)
                        """),
                        {
                            "call_id": call_result.get("call_id", "UNKNOWN"),
                            "phone": phone,
                            "message": message,
                            "scheme": scheme[0],
                            "status": "INITIATED" if call_result["success"] else "FAILED",
                            "language": language
                        }
                    )
                
                results.append(call_result)
            
            success_count = sum(1 for r in results if r["success"])
            
            return {
                "success": True,
                "total_calls": len(phone_numbers),
                "successful": success_count,
                "failed": len(phone_numbers) - success_count
            }
            
    except Exception as e:
        print(f"❌ Error sending scheme notifications: {e}")
        return {"success": False, "error": str(e)}


async def send_area_alert(
    area_name: str,
    alert_message: str,
    phone_numbers: List[str],
    language: str = "hindi"
):
    """
    Send alert to all citizens in a specific area.
    """
    try:
        # Generate message
        template = ALERT_TEMPLATES.get(language, ALERT_TEMPLATES["english"])
        message = template.format(
            area_name=area_name,
            alert_message=alert_message
        )
        
        # Make calls
        results = []
        for phone in phone_numbers:
            call_result = await create_retell_call(phone, message, language)
            
            # Log in database
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO outbound_calls
                        (call_id, phone_number, call_type, message_content,
                         alert_type, status, initiated_at, language)
                        VALUES
                        (:call_id, :phone, 'alert', :message,
                         :alert, :status, NOW(), :language)
                    """),
                    {
                        "call_id": call_result.get("call_id", "UNKNOWN"),
                        "phone": phone,
                        "message": message,
                        "alert": f"Area alert: {area_name}",
                        "status": "INITIATED" if call_result["success"] else "FAILED",
                        "language": language
                    }
                )
            
            results.append(call_result)
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "area": area_name,
            "total_calls": len(phone_numbers),
            "successful": success_count,
            "failed": len(phone_numbers) - success_count
        }
        
    except Exception as e:
        print(f"❌ Error sending area alert: {e}")
        return {"success": False, "error": str(e)}


async def send_complaint_follow_up(
    ticket_id: str,
    phone_number: str,
    citizen_name: str,
    update_message: str,
    language: str = "hindi"
):
    """
    Follow up with citizen about their complaint status.
    """
    try:
        # Generate message
        template = FOLLOW_UP_TEMPLATES.get(language, FOLLOW_UP_TEMPLATES["english"])
        message = template.format(
            name=citizen_name,
            ticket_id=ticket_id,
            update_message=update_message
        )
        
        # Make call
        call_result = await create_retell_call(phone_number, message, language)
        
        # Log in database
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO outbound_calls
                    (call_id, phone_number, call_type, message_content,
                     related_ticket_id, status, initiated_at, language)
                    VALUES
                    (:call_id, :phone, 'follow_up', :message,
                     :ticket, :status, NOW(), :language)
                """),
                {
                    "call_id": call_result.get("call_id", "UNKNOWN"),
                    "phone": phone_number,
                    "message": message,
                    "ticket": ticket_id,
                    "status": "INITIATED" if call_result["success"] else "FAILED",
                    "language": language
                }
            )
        
        return call_result
        
    except Exception as e:
        print(f"❌ Error sending follow-up: {e}")
        return {"success": False, "error": str(e)}


async def send_hotspot_alert_to_managers(area_name: str, level: str, open_complaints: int):
    """
    Alert managers about area hotspots.
    This sends calls to predefined manager numbers.
    """
    # Get manager phone numbers from environment or database
    manager_numbers = os.getenv("MANAGER_PHONE_NUMBERS", "").split(",")
    
    if not manager_numbers or not manager_numbers[0]:
        print("⚠️ No manager phone numbers configured")
        return
    
    message = f"""
Alert for managers: The area {area_name} has been flagged as a {level} hotspot 
with {open_complaints} open complaints. Immediate attention required.
"""
    
    for phone in manager_numbers:
        if phone.strip():
            await create_retell_call(phone.strip(), message, "english")


# ===================================================================
# SCHEDULED CAMPAIGNS
# ===================================================================

async def run_daily_scheme_campaign():
    """
    Daily automated campaign to notify citizens about active schemes.
    This should be called by a scheduler (cron job).
    """
    try:
        with engine.connect() as conn:
            # Get active schemes that need notifications
            result = conn.execute(
                text("""
                    SELECT scheme_code, scheme_name 
                    FROM government_schemes 
                    WHERE is_active = TRUE 
                      AND send_notifications = TRUE
                """)
            )
            
            schemes = result.fetchall()
            
            for scheme in schemes:
                # Get eligible phone numbers (example: from recent complaints)
                result = conn.execute(
                    text("""
                        SELECT DISTINCT contact 
                        FROM grievances 
                        WHERE contact IS NOT NULL 
                          AND created_at > NOW() - INTERVAL '30 days'
                        LIMIT 100
                    """)
                )
                
                phones = [row[0] for row in result if row[0]]
                
                if phones:
                    await send_scheme_notification(
                        scheme_code=scheme[0],
                        phone_numbers=phones,
                        language="hindi"
                    )
                    
                    print(f"✅ Sent scheme notifications for: {scheme[1]}")
        
    except Exception as e:
        print(f"❌ Error running scheme campaign: {e}")
