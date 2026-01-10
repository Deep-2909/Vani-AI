import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY is missing")

client = AsyncOpenAI(api_key=api_key)

# ===================================================================
# TOOL DEFINITIONS - Multiple tools for different intents
# ===================================================================

# Tool 1: Register New Grievance
REGISTER_GRIEVANCE_TOOL = {
    "type": "function",
    "function": {
        "name": "register_grievance",
        "description": "Register a new citizen grievance after explicit confirmation. Use this when the citizen wants to FILE A NEW COMPLAINT.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Citizen's full name as spoken"
                },
                "contact": {
                    "type": "string",
                    "description": "Citizen's 10-digit mobile number"
                },
                "issue": {
                    "type": "string",
                    "description": "Detailed description of the grievance"
                },
                "location": {
                    "type": "string",
                    "description": "Specific area/colony/sector where issue is occurring"
                },
                "department": {
                    "type": "string",
                    "enum": ["Water (DJB)", "Police", "Pollution (DPCC)", "Roads (PWD)", 
                             "Electricity", "Health", "Education", "Transport", "General/PGC"],
                    "description": "Government department responsible for this issue"
                },
                "category": {
                    "type": "string",
                    "enum": ["Water Supply", "Sewage/Drainage", "Road Maintenance", "Street Lights",
                             "Garbage Collection", "Traffic", "Law & Order", "Pollution", "Power Cut",
                             "Health Services", "Education", "Corruption/Harassment", "Billing Issues",
                             "Illegal Construction", "Encroachment", "Public Transport", "Other"],
                    "description": "Specific category of the grievance"
                },
                "priority": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High", "Critical"],
                    "description": "Priority level: Low (routine), Medium (needs attention), High (urgent), Critical (emergency/safety threat)"
                }
            },
            "required": ["name", "contact", "issue", "location", "department", "category", "priority"]
        }
    }
}

# Tool 2: Check Status of Existing Complaint
CHECK_STATUS_TOOL = {
    "type": "function",
    "function": {
        "name": "check_complaint_status",
        "description": "Check the status of an existing complaint. Use when citizen asks 'what is the status of my complaint' or provides a ticket ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "The complaint ticket ID (format: DEL-XXXXXX)"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Citizen's phone number for verification"
                }
            },
            "required": ["ticket_id"]
        }
    }
}

# Tool 3: Escalate Complaint
ESCALATE_COMPLAINT_TOOL = {
    "type": "function",
    "function": {
        "name": "escalate_complaint",
        "description": "Escalate an existing complaint to higher authorities. Use when citizen is dissatisfied or asks to escalate.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "The original complaint ticket ID"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for escalation (e.g., 'No action taken', 'Issue not resolved')"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Citizen's phone number for verification"
                }
            },
            "required": ["ticket_id", "reason"]
        }
    }
}

# Tool 4: Provide General Information
GENERAL_INFO_TOOL = {
    "type": "function",
    "function": {
        "name": "provide_general_info",
        "description": "Provide general information about government services, procedures, or helpline numbers. Use for informational queries.",
        "parameters": {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["office_hours", "helpline_numbers", "procedures", "eligibility", 
                             "documents_required", "online_services", "other"],
                    "description": "Type of information being requested"
                },
                "department": {
                    "type": "string",
                    "description": "Relevant department if applicable"
                }
            },
            "required": ["query_type"]
        }
    }
}

# Tool 5: Record Feedback
FEEDBACK_TOOL = {
    "type": "function",
    "function": {
        "name": "record_feedback",
        "description": "Record citizen feedback about resolved complaints or services. Use when citizen wants to give feedback or rate service.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "Related complaint ticket ID if applicable"
                },
                "rating": {
                    "type": "integer",
                    "description": "Rating from 1 (poor) to 5 (excellent)",
                    "enum": [1, 2, 3, 4, 5]
                },
                "feedback_text": {
                    "type": "string",
                    "description": "Detailed feedback from citizen"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Citizen's phone number"
                }
            },
            "required": ["rating", "feedback_text"]
        }
    }
}

# Tool 6: Emergency Assistance
EMERGENCY_TOOL = {
    "type": "function",
    "function": {
        "name": "emergency_assistance",
        "description": "Immediately escalate to human operator for emergencies. Use for life-threatening situations, crimes in progress, or critical safety issues.",
        "parameters": {
            "type": "object",
            "properties": {
                "emergency_type": {
                    "type": "string",
                    "enum": ["medical", "fire", "crime", "disaster", "accident", "other"],
                    "description": "Type of emergency"
                },
                "location": {
                    "type": "string",
                    "description": "Exact location of emergency"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Contact number"
                },
                "description": {
                    "type": "string",
                    "description": "Brief description of emergency"
                }
            },
            "required": ["emergency_type", "location", "phone_number", "description"]
        }
    }
}

# Combine all tools
ALL_TOOLS = [
    REGISTER_GRIEVANCE_TOOL,
    CHECK_STATUS_TOOL,
    ESCALATE_COMPLAINT_TOOL,
    GENERAL_INFO_TOOL,
    FEEDBACK_TOOL,
    EMERGENCY_TOOL
]


async def get_ai_response(
    messages: list, 
    context: str,
    user_confirmed: bool
):
    """
    Enhanced AI response with multi-intent detection.
    Automatically detects what the user wants to do and uses appropriate tools.
    """
    
    # Clean history
    clean_messages = [m for m in messages if m.get("role") != "system"]

    confirmation_block = (
        """
✅ THE USER HAS CONFIRMED.
You may now call the appropriate tool if all required details are present.
DO NOT ask for confirmation again.
"""
        if user_confirmed
        else
        """
⏸️ THE USER HAS NOT CONFIRMED YET.
DO NOT call any action tools (register, escalate, etc.) without explicit confirmation.
If you have all details for an action, ask: "Shall I proceed with this for you?"
"""
    )

    system_prompt = f"""
🎯 ROLE:
You are "Vani", the official AI Voice Assistant for the Government of NCT of Delhi.
You handle ALL types of citizen interactions intelligently.

📚 CONTEXT FROM OFFICIAL DOCUMENTS:
{context if context else "No specific documentation found."}

🗣️ VOICE GUIDELINES:
- Keep responses SHORT (max 2-3 sentences)
- Be warm, professional, and empathetic
- Use simple Hindi-English mix when appropriate
- NO bullet points, lists, or special characters in speech
- Speak naturally and conversationally

🎭 INTENT DETECTION:
Automatically detect what the citizen wants and use the appropriate tool:

1. **NEW COMPLAINT** → use register_grievance
   - Keywords: "register complaint", "file grievance", "report problem", "complaint hai"
   - Collect: name, contact, issue, location
   - Auto-categorize and set priority based on severity

2. **STATUS CHECK** → use check_complaint_status
   - Keywords: "check status", "what happened to my complaint", "ticket status", "DEL-"
   - Need: ticket ID

3. **ESCALATION** → use escalate_complaint
   - Keywords: "escalate", "not resolved", "no action taken", "speak to senior"
   - Need: ticket ID, reason

4. **GENERAL QUERY** → use provide_general_info
   - Keywords: "how to", "what is procedure", "helpline number", "office hours"
   - Provide: information from RAG context

5. **FEEDBACK** → use record_feedback
   - Keywords: "give feedback", "rate service", "complaint resolved", "satisfied"
   - Need: rating, feedback text

6. **EMERGENCY** → use emergency_assistance (IMMEDIATE)
   - Keywords: "emergency", "urgent", "someone injured", "fire", "crime happening now"
   - Immediately collect location and forward to human operator

🔍 AUTO-CATEGORIZATION RULES:

**Categories:**
- Water supply, sewage, drainage → "Water Supply" / "Sewage/Drainage"
- Potholes, broken roads → "Road Maintenance"
- Street lights not working → "Street Lights"
- Garbage not collected → "Garbage Collection"
- Traffic, parking → "Traffic"
- Theft, crime, harassment → "Law & Order"
- Air/noise/water pollution → "Pollution"
- Power cuts, no electricity → "Power Cut"
- Hospital, health issues → "Health Services"
- School, education → "Education"
- Bribery, corruption → "Corruption/Harassment"
- Wrong bill, overcharging → "Billing Issues"
- Unauthorized construction → "Illegal Construction"

**Priority Auto-Assignment:**
- **CRITICAL**: Life threatening, ongoing crime, major fire, severe accident, epidemic outbreak
- **HIGH**: No water for 24+ hours, sewage overflow, major road blockage, harassment, electricity failure affecting hospital/school
- **MEDIUM**: Water quality issues, street lights not working, moderate road damage, garbage not collected for 3+ days
- **LOW**: Minor issues, general inquiries, cosmetic problems

**Department Mapping:**
- Water, sewage → "Water (DJB)"
- Crime, harassment, traffic → "Police"
- Pollution → "Pollution (DPCC)"
- Roads, potholes → "Roads (PWD)"
- Electricity → "Electricity"
- Health → "Health"
- Education → "Education"

📋 REQUIRED INFORMATION FOR NEW COMPLAINTS:
Must collect ALL before calling register_grievance:
✓ Citizen's full name
✓ Mobile number (10 digits)
✓ Detailed issue description
✓ Specific location/area
✓ Auto-determine: department, category, priority

❗ CRITICAL RULES:
1. Never assume or guess citizen's name/number
2. Ask only ONE missing detail at a time
3. For EMERGENCIES: Collect location immediately and escalate
4. Always confirm before taking action
5. If user provides ticket ID, assume status check intent
6. Be empathetic - citizens are often frustrated

{confirmation_block}

💬 EXAMPLE INTERACTIONS:

User: "I want to check my complaint status, ticket DEL-ABC123"
→ Call check_complaint_status immediately

User: "There's a fire in sector 15!"
→ Call emergency_assistance immediately, don't waste time

User: "Water problem in my area"
→ Collect details for register_grievance, auto-categorize as "Water Supply"

User: "My complaint not resolved, escalate it"
→ Ask for ticket ID, then call escalate_complaint

User: "What is the helpline number for DJB?"
→ Call provide_general_info to retrieve from RAG
"""

    full_messages = [{"role": "system", "content": system_prompt}] + clean_messages

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        tools=ALL_TOOLS,
        tool_choice="auto",
        temperature=0.2,
        max_tokens=250
    )

    msg = response.choices[0].message

    spoken_text = ""
    if isinstance(msg.content, str):
        spoken_text = msg.content.strip()

    if not spoken_text and not msg.tool_calls:
        spoken_text = "I'm sorry, could you please repeat that?"

    tool_calls = []
    if msg.tool_calls:
        for t in msg.tool_calls:
            tool_calls.append({
                "name": t.function.name,
                "arguments": t.function.arguments
            })
            print(f"🔧 TOOL CALLED: {t.function.name}")
            print(f"   Arguments: {t.function.arguments}")

    return {
        "content": spoken_text,
        "tool_calls": tool_calls
    }
