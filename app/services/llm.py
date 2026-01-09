import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY is missing")

client = AsyncOpenAI(api_key=api_key)

# --- TOOL DEFINITION ---
GRIEVANCE_TOOL = {
    "type": "function",
    "function": {
        "name": "register_grievance",
        "description": "Register a formal citizen grievance after explicit confirmation.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Citizen's name as spoken by the citizen. Do NOT guess."
                },
                "issue": {
                    "type": "string",
                    "description": "Exact grievance description in the citizen's own words."
                },
                "department": {
                    "type": "string",
                    "enum": ["Water (DJB)", "Police", "Pollution (DPCC)", "General/PGC"]
                },
                "urgency": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High"],
                    "default": "Medium"
                }
            },
            "required": ["name", "issue", "department"]
        }
    }
}


async def get_ai_response(
    user_query: str,
    context: str,
    user_confirmed: bool
):
    confirmation_block = (
        """
THE USER HAS CONFIRMED.
You may call the register_grievance tool IF all required details are present.
DO NOT ask for confirmation again.
"""
        if user_confirmed
        else
        """
THE USER HAS NOT CONFIRMED YET.
DO NOT call the register_grievance tool.
If details are complete, ask for confirmation politely.
"""
    )

    system_prompt = f"""
ROLE:
You are "Vani", the official AI Voice Assistant for the Government of NCT of Delhi.

CONTEXT FROM OFFICIAL DOCUMENTS:
{context}

VOICE RULES:
- Max 2 short sentences
- Clear and polite
- No bullet points

CRITICAL RULES:
1. Never assume the citizen's name
2. Ask only one missing detail at a time
3. Never invent information

{confirmation_block}
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        tools=[GRIEVANCE_TOOL],
        tool_choice="auto",
        temperature=0.3
    )

    msg = response.choices[0].message

    spoken_text = msg.content if isinstance(msg.content, str) else ""
    if not spoken_text.strip():
        spoken_text = "Please tell me your name and describe your complaint."

    tool_calls = []
    if msg.tool_calls:
        for t in msg.tool_calls:
            tool_calls.append({
                "name": t.function.name,
                "arguments": t.function.arguments
            })

    return {
        "content": spoken_text,
        "tool_calls": tool_calls
    }
