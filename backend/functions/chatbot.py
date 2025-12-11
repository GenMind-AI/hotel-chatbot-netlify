import json
import os
from datetime import datetime, timedelta
from dateparser.search import search_dates
from openai import OpenAI
import requests

# Read Environment Vars (Netlify dashboard)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HOTEL_API_ENDPOINT = "https://hotel.dev-maister.gr/hotel_Casa/mcp_server/index.php"
HOTEL_API_BEARER_TOKEN = os.getenv("HOTEL_API_BEARER_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------
#  HOTEL AVAILABILITY
# -------------------------
def get_hotel_availability(json_key: str, start: str, end: str, adults: str, kids: str, minors: str):
    headers = {
        "Authorization": f"Bearer {HOTEL_API_BEARER_TOKEN}",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0"
    }
    params = {
        "json_key": json_key,
        "start": start,
        "end": end,
        "adults": adults,
        "kids": kids,
        "minors": minors
    }
    try:
        response = requests.get(HOTEL_API_ENDPOINT, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": "API call failed", "details": str(e)}

# -------------------------
#  HOTEL PRICE
# -------------------------
def get_hotel_price(json_key: str, start: str, end: str, adults: str, kids: str, minors: str):
    headers = {
        "Authorization": f"Bearer {HOTEL_API_BEARER_TOKEN}",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0"
    }
    params = {
        "json_key": json_key,
        "start": start,
        "end": end,
        "adults": adults,
        "kids": kids,
        "minors": minors
    }
    try:
        response = requests.get(HOTEL_API_ENDPOINT, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": "API call failed", "details": str(e)}

# -------------------------
#  TOOLS
# -------------------------
tool_availability = {
    "name": "get_hotel_availability",
    "description": "Get hotel room availability",
    "parameters": {
        "type": "object",
        "properties": {
            "json_key": {"type": "string"},
            "start": {"type": "string"},
            "end": {"type": "string"},
            "adults": {"type": "string"},
            "kids": {"type": "string"},
            "minors": {"type": "string"}
        },
        "required": ["json_key", "start", "end", "adults", "kids", "minors"]
    }
}

tool_price = {
    "name": "get_hotel_price",
    "description": "Get hotel room prices",
    "parameters": {
        "type": "object",
        "properties": {
            "json_key": {"type": "string"},
            "start": {"type": "string"},
            "end": {"type": "string"},
            "adults": {"type": "string"},
            "kids": {"type": "string"},
            "minors": {"type": "string"}
        },
        "required": ["json_key", "start", "end", "adults", "kids", "minors"]
    }
}

system_prompt = """
You are a hotel reception assistant for Hotel Ilion.
You can chat naturally...
(unchanged)
"""

# -------------------------
#  GPT WRAPPER
# -------------------------
def call_gpt(messages, tools=None):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        functions=(tools if tools else []),
        function_call="auto"
    )
    return resp.choices[0].message

# -------------------------
#  PROCESS TOOL CALL
# -------------------------
def try_handle_tool_call(ai_message):
    fc = ai_message.function_call
    if not fc:
        return None

    args = json.loads(fc.arguments or "{}")

    if fc.name == "get_hotel_availability":
        result = get_hotel_availability(**args)
        return {"role": "function", "name": fc.name, "content": json.dumps(result)}

    if fc.name == "get_hotel_price":
        result = get_hotel_price(**args)
        return {"role": "function", "name": fc.name, "content": json.dumps(result)}

    return None

# =================================================
#  NETLIFY FUNCTION HTTP HANDLER
# =================================================
def handler(event, context):

    try:
        body = json.loads(event.get("body", "{}"))
        user_message = body.get("message", "")
        conversation = body.get("messages", [])

        if not conversation:
            conversation = [{"role": "system", "content": system_prompt}]

        conversation.append({"role": "user", "content": user_message})

        ai_msg = call_gpt(conversation, tools=[tool_availability, tool_price])
        conversation.append({
            "role": "assistant",
            "content": ai_msg.content,
            "function_call": ai_msg.function_call
        })

        tool_response = try_handle_tool_call(ai_msg)

        if tool_response:
            conversation.append(tool_response)
            ai_msg2 = call_gpt(conversation, tools=[tool_availability, tool_price])
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "response": ai_msg2.content,
                    "messages": conversation
                })
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "response": ai_msg.content,
                "messages": conversation
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
