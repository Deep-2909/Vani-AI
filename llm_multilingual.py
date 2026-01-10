import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY is missing")

client = AsyncOpenAI(api_key=api_key)

# ===================================================================
# LANGUAGE DETECTION AND RESPONSE
# ===================================================================

LANGUAGE_INSTRUCTIONS = {
    "hindi": {
        "greeting": "Namaste, main Vani hoon Delhi Sarkar ki AI Voice Assistant. Main aapki kaise madad kar sakti hoon?",
        "system_note": "Respond in HINGLISH (Hindi-English mix). Use simple Hindi words mixed with English for technical terms. Example: 'Aapki complaint register ho gayi hai' instead of pure English."
    },
    "punjabi": {
        "greeting": "Sat Sri Akal, main Vani haan Delhi Sarkar di AI Voice Assistant. Main tussi ki madad kar sakdi haan?",
        "system_note": "Respond in PUNGLISH (Punjabi-English mix). Use simple Punjabi words mixed with English. Example: 'Tuhadi complaint register ho gayi hai'."
    },
    "english": {
        "greeting": "Hello, I am Vani, the AI Voice Assistant for Delhi Government. How can I help you?",
        "system_note": "Respond in clear, simple English."
    }
}

# ===================================================================
# TOOL DEFINITIONS
# ===================================================================

# All previous tools remain the same
REGISTER_GRIEVANCE_TOOL = {
    "type": "function",
    "function": {
        "name": "register_grievance",
        "description": "Register a new citizen grievance after explicit confirmation.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Citizen's full name"},
                "contact": {"type": "string", "description": "10-digit mobile number"},
                "issue": {"type": "string", "description": "Detailed grievance description"},
                "location": {"type": "string", "description": "Specific area/colony/sector"},
                "department": {
                    "type": "string",
                    "enum": ["Water (DJB)", "Police", "Pollution (DPCC)", "Roads (PWD)", 
                             "Electricity", "Health", "Education", "Transport", "General/PGC"]
                },
                "category": {
                    "type": "string",
                    "enum": ["Water Supply", "Sewage/Drainage", "Road Maintenance", "Street Lights",
                             "Garbage Collection", "Traffic", "Law & Order", "Pollution", "Power Cut",
                             "Health Services", "Education", "Corruption/Harassment", "Billing Issues",
                             "Illegal Construction", "Encroachment", "Public Transport", "Other"]
                },
                "priority": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High", "Critical"]
                }
            },
            "required": ["name", "contact", "issue", "location", "department", "category", "priority"]
        }
    }
}

CHECK_STATUS_TOOL = {
    "type": "function",
    "function": {
        "name": "check_complaint_status",
        "description": "Check status of existing complaint",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "phone_number": {"type": "string"}
            },
            "required": ["ticket_id"]
        }
    }
}

ESCALATE_COMPLAINT_TOOL = {
    "type": "function",
    "function": {
        "name": "escalate_complaint",
        "description": "Escalate complaint to higher authorities",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "reason": {"type": "string"},
                "phone_number": {"type": "string"}
            },
            "required": ["ticket_id", "reason"]
        }
    }
}

GENERAL_INFO_TOOL = {
    "type": "function",
    "function": {
        "name": "provide_general_info",
        "description": "Provide general information",
        "parameters": {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["office_hours", "helpline_numbers", "procedures", "eligibility", 
                             "documents_required", "online_services", "other"]
                },
                "department": {"type": "string"}
            },
            "required": ["query_type"]
        }
    }
}

FEEDBACK_TOOL = {
    "type": "function",
    "function": {
        "name": "record_feedback",
        "description": "Record citizen feedback",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "rating": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                "feedback_text": {"type": "string"},
                "phone_number": {"type": "string"}
            },
            "required": ["rating", "feedback_text"]
        }
    }
}

EMERGENCY_TOOL = {
    "type": "function",
    "function": {
        "name": "emergency_assistance",
        "description": "Immediate emergency escalation",
        "parameters": {
            "type": "object",
            "properties": {
                "emergency_type": {
                    "type": "string",
                    "enum": ["medical", "fire", "crime", "disaster", "accident", "other"]
                },
                "location": {"type": "string"},
                "phone_number": {"type": "string"},
                "description": {"type": "string"}
            },
            "required": ["emergency_type", "location", "phone_number", "description"]
        }
    }
}

ALL_TOOLS = [
    REGISTER_GRIEVANCE_TOOL,
    CHECK_STATUS_TOOL,
    ESCALATE_COMPLAINT_TOOL,
    GENERAL_INFO_TOOL,
    FEEDBACK_TOOL,
    EMERGENCY_TOOL
]


def detect_language(text: str) -> str:
    """
    Detect language from user input.
    Returns: 'hindi', 'punjabi', or 'english'
    """
    text_lower = text.lower()
    
    # Hindi indicators
    hindi_words = ['namaste', 'dhanyavaad', 'shukriya', 'kaise', 'kya', 'hai', 'hoon', 
                   'aapki', 'mera', 'complaint', 'paani', 'bijli', 'saaf', 'ganda']
    
    # Punjabi indicators
    punjabi_words = ['sat sri akal', 'satsriakal', 'tuhadi', 'tussi', 'ki', 'haan', 
                     'haiga', 'karde', 'karna']
    
    # Check for Devanagari script (Hindi)
    if any('\u0900' <= char <= '\u097F' for char in text):
        return 'hindi'
    
    # Check for Gurmukhi script (Punjabi)
    if any('\u0A00' <= char <= '\u0A7F' for char in text):
        return 'punjabi'
    
    # Check for keyword matches
    hindi_score = sum(1 for word in hindi_words if word in text_lower)
    punjabi_score = sum(1 for word in punjabi_words if word in text_lower)
    
    if punjabi_score > hindi_score:
        return 'punjabi'
    elif hindi_score > 0:
        return 'hindi'
    
    return 'english'


async def get_ai_response(
    messages: list, 
    context: str,
    user_confirmed: bool,
    language: str = None
):
    """
    Enhanced AI response with multilingual support.
    """
    
    # Detect language from latest user message if not specified
    if not language:
        latest_msg = next((m['content'] for m in reversed(messages) if m.get('role') == 'user'), '')
        language = detect_language(latest_msg)
    
    # Get language-specific instructions
    lang_config = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS['english'])
    
    # Clean history
    clean_messages = [m for m in messages if m.get("role") != "system"]

    confirmation_block = (
        """
✅ USER HAS CONFIRMED.
Call the appropriate tool if all required details are present.
"""
        if user_confirmed
        else
        """
⏸️ USER HAS NOT CONFIRMED YET.
Do not call action tools without confirmation.
"""
    )

    system_prompt = f"""
🎯 ROLE:
You are "Vani", the official AI Voice Assistant for the Government of NCT of Delhi.
You are multilingual and can communicate in Hindi, Punjabi, and English.

🗣️ LANGUAGE: {language.upper()}
{lang_config['system_note']}

IMPORTANT LANGUAGE RULES:
- Detect and match the user's language naturally
- For Hindi speakers: Use Hinglish (Hindi + English mix)
- For Punjabi speakers: Use Punglish (Punjabi + English mix)  
- For English speakers: Use clear, simple English
- NEVER force pure Hindi/Punjabi - always mix with English for clarity
- Keep responses SHORT (2-3 sentences maximum)

MULTILINGUAL EXAMPLES:

Hindi Response Style:
"Aapki complaint register ho gayi hai. Ticket number hai DEL-ABC123. Aapko SMS updates milenge."

Punjabi Response Style:
"Tuhadi complaint register ho gayi hai. Ticket number hai DEL-ABC123. Tuhanu SMS updates milange."

English Response Style:
"Your complaint has been registered. Ticket number is DEL-ABC123. You will receive SMS updates."

📚 CONTEXT FROM DOCUMENTS:
{context if context else "No specific documentation found."}

🎭 INTENT DETECTION & TOOLS:
[Same as before - all 6 intents]

1. NEW COMPLAINT → register_grievance
2. STATUS CHECK → check_complaint_status
3. ESCALATION → escalate_complaint
4. GENERAL QUERY → provide_general_info
5. FEEDBACK → record_feedback
6. EMERGENCY → emergency_assistance

🔍 AUTO-CATEGORIZATION & PRIORITY:
[Same rules as before]

📋 REQUIRED INFO FOR COMPLAINTS:
✓ Name
✓ Mobile (10 digits)
✓ Issue description
✓ Location/area
✓ Auto-determine: department, category, priority

{confirmation_block}

💬 LANGUAGE-SPECIFIC PHRASES:

HINDI:
- Greeting: "Namaste, main Vani hoon. Aapki kaise madad kar sakti hoon?"
- Ask name: "Kripya apna naam bataiye?"
- Ask location: "Aap kis area se call kar rahe hain?"
- Confirm: "Kya main aapki complaint register kar doon?"
- Success: "Aapki complaint register ho gayi hai."

PUNJABI:
- Greeting: "Sat Sri Akal, main Vani haan. Tussi ki madad chahiye?"
- Ask name: "Apna naam dasso ji?"
- Ask location: "Tussi kithon call kar rahe ho?"
- Confirm: "Ki main tuhadi complaint register kar doon?"
- Success: "Tuhadi complaint register ho gayi hai."

ENGLISH:
- Greeting: "Hello, I am Vani. How can I help you?"
- Ask name: "Could you please tell me your name?"
- Ask location: "Which area are you calling from?"
- Confirm: "Shall I register this complaint?"
- Success: "Your complaint has been registered."

VOICE GUIDELINES:
- Natural conversational tone
- Short sentences (max 2-3)
- No bullet points or special characters
- Use numbers in words ("nine eight seven" not "987")
- Be warm and empathetic
"""

    full_messages = [{"role": "system", "content": system_prompt}] + clean_messages

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        tools=ALL_TOOLS,
        tool_choice="auto",
        temperature=0.3,  # Slightly higher for natural multilingual responses
        max_tokens=250
    )

    msg = response.choices[0].message

    spoken_text = ""
    if isinstance(msg.content, str):
        spoken_text = msg.content.strip()

    if not spoken_text and not msg.tool_calls:
        # Fallback in detected language
        fallbacks = {
            'hindi': "Maaf kijiye, kya aap phir se bol sakte hain?",
            'punjabi': "Maaf karna ji, tussi phir bol sakde ho?",
            'english': "I'm sorry, could you please repeat that?"
        }
        spoken_text = fallbacks.get(language, fallbacks['english'])

    tool_calls = []
    if msg.tool_calls:
        for t in msg.tool_calls:
            tool_calls.append({
                "name": t.function.name,
                "arguments": t.function.arguments
            })

    return {
        "content": spoken_text,
        "tool_calls": tool_calls,
        "detected_language": language
    }
