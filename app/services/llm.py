import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY is missing")

client = AsyncOpenAI(api_key=api_key)

# --- ENHANCED TOOL DEFINITION ---
GRIEVANCE_TOOL = {
    "type": "function",
    "function": {
        "name": "register_grievance",
        "description": "Register a formal citizen grievance after explicit confirmation and ALL required details are collected.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Citizen's full name as spoken by the citizen. Do NOT guess or assume."
                },
                "issue": {
                    "type": "string",
                    "description": "Detailed grievance description in the citizen's own words, including what happened and when."
                },
                "location": {
                    "type": "string",
                    "description": "Specific location/address/area where the issue is occurring (colony name, street, landmark, ward number, etc.)"
                },
                "contact": {
                    "type": "string",
                    "description": "Citizen's mobile number for updates and follow-up"
                },
                "department": {
                    "type": "string",
                    "enum": ["Water (DJB)", "Police", "Pollution (DPCC)", "Roads (PWD)", "Electricity", "General/PGC"],
                    "description": "The government department responsible for this issue"
                },
                "urgency": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High", "Emergency"],
                    "default": "Medium",
                    "description": "Urgency level based on issue severity"
                }
            },
            "required": ["name", "issue", "location", "contact", "department"]
        }
    }
}


async def get_ai_response(
    messages: list, 
    context: str,
    user_confirmed: bool
):
    """
    Get AI response using GPT-4 with RAG context and tool calling.
    
    Args:
        messages: Conversation history
        context: RAG context from Pinecone
        user_confirmed: Whether user has confirmed registration
    
    Returns:
        dict with 'content' (spoken text) and 'tool_calls' (if any)
    """
    
    # Clean history: Remove any existing 'system' messages to prevent duplication
    clean_messages = [m for m in messages if m.get("role") != "system"]

    # Confirmation logic
    confirmation_block = (
        """
✅ THE USER HAS CONFIRMED.
You may call the register_grievance tool IF and ONLY IF all required details are present:
- name
- issue (detailed description)
- location (specific area/address)
- contact (mobile number)
- department

DO NOT ask for confirmation again.
DO NOT call the tool if ANY detail is missing.
"""
        if user_confirmed
        else
        """
⏸️ THE USER HAS NOT CONFIRMED YET.
DO NOT call the register_grievance tool under any circumstances.
If you have all details, politely ask: "Shall I register this complaint for you?"
"""
    )

    system_prompt = f"""
🎯 ROLE:
You are "Vani", the official AI Voice Assistant for the Government of NCT of Delhi.
You help citizens register grievances across all government departments.

📚 CONTEXT FROM OFFICIAL DOCUMENTS:
{context if context else "No specific documentation found for this query."}

🗣️ VOICE GUIDELINES:
- Keep responses SHORT (max 2-3 sentences)
- Be warm, professional, and empathetic
- Use simple Hindi-English mixed language when appropriate (e.g., "Namaste", "dhanyavaad")
- NO bullet points, lists, or special characters in speech
- Speak naturally as a helpful government representative would

🔴 CRITICAL RULES FOR REGISTRATION:

1. REQUIRED INFORMATION (must collect ALL before registering):
   ✓ Citizen's full name
   ✓ Mobile number (10 digits)
   ✓ Detailed issue description
   ✓ Specific location/address/area (colony, street, landmark, ward)
   ✓ Department (infer from issue or ask)

2. CONVERSATION FLOW:
   - Ask for ONE missing detail at a time
   - Be conversational, not robotic
   - If user provides multiple details at once, acknowledge all
   - Example: "Thank you. And which area are you calling from?"

3. DEPARTMENT CLASSIFICATION:
   - Water supply, sewage, drainage → "Water (DJB)"
   - Law & order, crime, traffic → "Police"
   - Air quality, noise, waste → "Pollution (DPCC)"
   - Potholes, roads, bridges → "Roads (PWD)"
   - Power cuts, billing → "Electricity"
   - Other issues → "General/PGC"

4. LOCATION IS MANDATORY:
   - ALWAYS ask for specific location/area
   - Examples: "Which colony?", "Which area are you calling from?", "Can you tell me the location?"
   - Don't accept vague answers like "Delhi" or "my area"

5. NEVER:
   - Assume or guess any information
   - Invent details the citizen didn't provide
   - Register without explicit confirmation
   - Use the citizen's exact words from previous messages as "confirmation"

{confirmation_block}

📱 AFTER REGISTRATION:
Once the grievance tool is called successfully, tell the citizen:
"Your complaint has been registered with ticket number [ID]. You will receive SMS updates. Is there anything else I can help you with?"

💡 EXAMPLE CONVERSATIONS:

Good:
User: "I want to complain about dirty water"
You: "I understand. Could you please tell me your name?"
User: "Rajesh Kumar"
You: "Thank you Rajesh ji. Which area are you calling from?"
User: "Rohini Sector 7"
You: "And what is your mobile number?"
User: "9876543210"
You: "Thank you. Can you describe the water issue in more detail?"
User: "The water is brown and smells bad since 3 days"
You: "I understand this is concerning. Shall I register this complaint with the Delhi Jal Board for you?"
User: "Yes please"
[Tool called with all details]

Bad:
User: "Water problem"
You: "Registering your complaint now" ❌ (missing ALL details!)
"""

    # Construct full message history
    full_messages = [{"role": "system", "content": system_prompt}] + clean_messages

    # Call OpenAI with tool support
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=full_messages,
            tools=[GRIEVANCE_TOOL],
            tool_choice="auto",
            temperature=0.2,  # Slightly higher for more natural conversation
            max_tokens=200    # Limit for concise voice responses
        )

        msg = response.choices[0].message

        # Extract spoken content
        spoken_text = ""
        if isinstance(msg.content, str):
            spoken_text = msg.content.strip()

        # Fallback if no content
        if not spoken_text and not msg.tool_calls:
            spoken_text = "I'm sorry, could you please repeat that?"

        # Extract tool calls
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

    except Exception as e:
        print(f"❌ LLM ERROR: {e}")
        return {
            "content": "I apologize, I'm having technical difficulties. Please try again.",
            "tool_calls": []
        }