"""
PATCH: Flexible Ticket ID Matching
Add this function to your retell_ws.py to handle different ticket formats
"""

def normalize_ticket_id(ticket_id: str) -> str:
    """
    Normalize ticket ID to match database format.
    Handles:
    - "DELDBE1A6" → "DEL-DBE1A6"
    - "del dbe 1a6" → "DEL-DBE1A6"
    - "D E L D B E 1 A 6" → "DEL-DBE1A6"
    """
    # Remove all spaces and convert to uppercase
    ticket_id = ticket_id.replace(" ", "").upper()
    
    # If it starts with DEL but no hyphen, add it
    if ticket_id.startswith("DEL") and len(ticket_id) > 3:
        # Check if hyphen is missing
        if ticket_id[3] != "-":
            # Add hyphen after DEL
            ticket_id = "DEL-" + ticket_id[3:]
    
    return ticket_id


# ============================================================================
# UPDATED STATUS CHECK SECTION
# Replace the status check code (around line 265) with this:
# ============================================================================

elif tool_name == "check_complaint_status":
    # Get ticket ID from args
    raw_ticket_id = args.get("ticket_id", "")
    
    # Normalize the ticket ID (handles different formats)
    ticket_id = normalize_ticket_id(raw_ticket_id)
    
    print(f"\n🔍 CHECKING STATUS:")
    print(f"   User said: {raw_ticket_id}")
    print(f"   Normalized: {ticket_id}")

    with engine.begin() as conn:
        # Log the status check
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
        
        # Try flexible search - match with or without hyphen
        result = conn.execute(
            text("""
                SELECT ticket_id, status, description, department, 
                       category, priority, created_at, resolved_at
                FROM grievances 
                WHERE ticket_id = :ticket_id
                   OR REPLACE(ticket_id, '-', '') = REPLACE(:ticket_id, '-', '')
                LIMIT 1
            """),
            {"ticket_id": ticket_id}
        )
        
        complaint = result.fetchone()

    if complaint:
        # Found the complaint!
        actual_ticket_id = complaint[0]  # Get actual ticket ID from DB
        status = complaint[1]
        dept = complaint[3]
        priority = complaint[5]
        
        print(f"   ✅ Found: {actual_ticket_id}")
        
        # Multilingual status responses
        if response_language == "hindi":
            status_messages = {
                "OPEN": "currently open hai aur review ho rahi hai",
                "IN_PROGRESS": "in progress hai aur handle ho rahi hai",
                "RESOLVED": "resolve ho gayi hai",
                "CLOSED": "close ho gayi hai",
                "ESCALATED": "escalate kar di gayi hai higher authorities ko"
            }
            spoken_text = (
                f"Aapki complaint ticket number {actual_ticket_id} "
                f"{status_messages.get(status, 'process ho rahi hai')} "
                f"{dept} dwara. "
                f"Yeh ek {priority} priority issue hai. "
                f"Kya aur kuch janna chahte hain?"
            )
        elif response_language == "punjabi":
            status_messages = {
                "OPEN": "open hai te review ho rahi hai",
                "IN_PROGRESS": "progress vich hai",
                "RESOLVED": "resolve ho gayi hai",
                "CLOSED": "close ho gayi hai",
                "ESCALATED": "escalate ho gayi hai"
            }
            spoken_text = (
                f"Tuhadi complaint ticket number {actual_ticket_id} "
                f"{status_messages.get(status, 'process ho rahi hai')} "
                f"{dept} valon. "
                f"Eh ek {priority} priority issue hai. "
                f"Ki hor kuch janna chahunde ho?"
            )
        else:
            status_messages = {
                "OPEN": "is currently open and being reviewed by",
                "IN_PROGRESS": "is in progress and being handled by",
                "RESOLVED": "has been resolved by",
                "CLOSED": "has been closed by",
                "ESCALATED": "has been escalated to higher authorities in"
            }
            spoken_text = (
                f"Your complaint with ticket number {actual_ticket_id} "
                f"{status_messages.get(status, 'is being processed by')} "
                f"{dept}. "
                f"This is a {priority} priority issue. "
                f"Is there anything else I can help you with?"
            )
    else:
        # Not found - provide helpful message
        print(f"   ❌ Not found: {ticket_id}")
        
        if response_language == "hindi":
            spoken_text = (
                f"Maaf kijiye, mujhe {ticket_id} ticket number ki koi complaint nahi mili. "
                f"Kripya ticket number dobara check karein. "
                f"Ticket number DEL se shuru hota hai jaise DEL-ABC123. "
                f"Kya main aur kuch madad kar sakti hoon?"
            )
        elif response_language == "punjabi":
            spoken_text = (
                f"Maaf karna, mujhe {ticket_id} ticket number di koi complaint nahi mili. "
                f"Meharbani karke ticket number phir check karo. "
                f"Ki main hor kuch madad kar sakdi haan?"
            )
        else:
            spoken_text = (
                f"I could not find a complaint with ticket number {ticket_id}. "
                f"Please check the ticket number and try again. "
                f"Ticket numbers start with DEL, like DEL-ABC123. "
                f"Is there anything else I can help you with?"
            )
    
    print(f"✅ Status check completed")
