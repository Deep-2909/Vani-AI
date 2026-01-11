"""
Retell API Service
Fetches call details and transcripts from Retell AI
"""
import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
RETELL_API_BASE = "https://api.retellai.com/v2"


def fetch_call_transcript(call_id: str) -> Optional[str]:
    """
    Fetch the full transcript for a call from Retell API.

    Args:
        call_id: The Retell call ID

    Returns:
        Formatted transcript string or None if not available
    """
    if not RETELL_API_KEY:
        print("⚠️ RETELL_API_KEY not found in environment")
        return None

    # Strip any quotes or spaces from the API key
    api_key = RETELL_API_KEY.strip().strip('"').strip("'")
    print(f"🔑 Using Retell API Key: {api_key[:10]}...")

    try:
        url = f"{RETELL_API_BASE}/get-call/{call_id}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print(f"📞 Calling Retell API: GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📥 Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            transcript_list = data.get("transcript", [])

            print(f"📝 Transcript entries found: {len(transcript_list)}")

            if not transcript_list:
                print("⚠️ Transcript list is empty")
                return None

            # Format transcript as conversation
            formatted_transcript = format_transcript(transcript_list)
            print(f"✅ Formatted transcript length: {len(formatted_transcript)} chars")
            return formatted_transcript

        elif response.status_code == 404:
            print(f"⚠️ Call {call_id} not found in Retell")
            return None

        else:
            print(f"❌ Retell API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error fetching transcript for call {call_id}: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_transcript(transcript_list: list) -> str:
    """
    Format Retell transcript list into readable conversation.

    Args:
        transcript_list: List of transcript entries from Retell

    Returns:
        Formatted string with speaker labels
    """
    formatted_lines = []

    for entry in transcript_list:
        role = entry.get("role", "unknown")
        content = entry.get("content", "").strip()

        if not content:
            continue

        # Map roles to readable labels
        if role == "agent":
            speaker = "🤖 Agent"
        elif role == "user":
            speaker = "👤 User"
        else:
            speaker = f"❓ {role.capitalize()}"

        formatted_lines.append(f"{speaker}: {content}")

    return "\n\n".join(formatted_lines)


def get_call_details(call_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch complete call details from Retell API.

    Args:
        call_id: The Retell call ID

    Returns:
        Dictionary with call details or None if not available
    """
    if not RETELL_API_KEY:
        print("⚠️ RETELL_API_KEY not found in environment")
        return None

    try:
        url = f"{RETELL_API_BASE}/get-call/{call_id}"
        headers = {
            "Authorization": f"Bearer {RETELL_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Retell API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error fetching call details: {e}")
        return None
