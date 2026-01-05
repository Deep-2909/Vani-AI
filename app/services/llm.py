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
        "description": (
            "Use this ONLY after the citizen has clearly confirmed that they want to "
            "register a formal grievance AND has explicitly provided their name, issue, "
            "and department."
        ),
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


async def get_ai_response(user_query: str, context: str):
    """
    Generates a voice-optimized assistant response and optional tool call.
    """

    system_prompt = f"""
ROLE:
You are "Vani", the official AI Voice Assistant for the Government of NCT of Delhi.

CONTEXT FROM OFFICIAL DOCUMENTS:
{context}

VOICE RULES (VERY IMPORTANT):
- Max 2 short sentences per response.
- No bullet points.
- No long explanations.
- Speak clearly and politely.

CRITICAL OPERATIONAL RULES:
1. NEVER assume or invent the citizen's name.
2. NEVER call the register_grievance tool unless the citizen has:
   a) Explicitly said they want to register a complaint, AND
   b) Clearly provided their name, AND
   c) Clearly described the issue.
3. If any required detail is missing, ASK ONE QUESTION AT A TIME.
4. Before calling the tool, always ask:
   "Shall I go ahead and register this complaint for you?"
5. If the citizen agrees, THEN call the tool.

If the citizen is only asking for information, DO NOT call any tool.
"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        tools=[GRIEVANCE_TOOL],
        tool_choice="auto"
    )

    msg = response.choices[0].message

    return {
    "content": msg.content if isinstance(msg.content, str) else "",
    "tool_calls": msg.tool_calls or []
    }

