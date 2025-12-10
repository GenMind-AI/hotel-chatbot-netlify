from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import hotel_agent  # import your exact file (hotel_agent.py)

app = Flask(__name__)
# In production replace '*' with the exact domain(s) of your widget to tighten security
CORS(app, resources={r"/*": {"origins": "*"}})

# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# Expose availability endpoint
@app.route("/availability", methods=["GET", "POST"])
def availability():
    # Accept both GET (query params) and POST (json body)
    if request.method == "GET":
        args = request.args
        json_key = args.get("json_key")
        start = args.get("start")
        end = args.get("end")
        adults = args.get("adults")
        kids = args.get("kids")
        minors = args.get("minors")
    else:
        body = request.get_json(force=True, silent=True) or {}
        json_key = body.get("json_key")
        start = body.get("start")
        end = body.get("end")
        adults = body.get("adults")
        kids = body.get("kids")
        minors = body.get("minors")

    # Basic validation
    if not all([json_key, start, end, adults is not None, kids is not None, minors is not None]):
        return jsonify({"error": "missing required parameters"}), 400

    try:
        result = hotel_agent.get_hotel_availability(json_key, start, end, adults, kids, minors)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "internal_error", "details": str(e)}), 500

# Expose price endpoint
@app.route("/price", methods=["GET", "POST"])
def price():
    if request.method == "GET":
        args = request.args
        json_key = args.get("json_key")
        start = args.get("start")
        end = args.get("end")
        adults = args.get("adults")
        kids = args.get("kids")
        minors = args.get("minors")
    else:
        body = request.get_json(force=True, silent=True) or {}
        json_key = body.get("json_key")
        start = body.get("start")
        end = body.get("end")
        adults = body.get("adults")
        kids = body.get("kids")
        minors = body.get("minors")

    if not all([json_key, start, end, adults is not None, kids is not None, minors is not None]):
        return jsonify({"error": "missing required parameters"}), 400

    try:
        result = hotel_agent.get_hotel_price(json_key, start, end, adults, kids, minors)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "internal_error", "details": str(e)}), 500

# Optional: expose a single /chat proxy if you later want the widget to send chat messages
@app.route("/chat", methods=["POST"])
def chat_proxy():
    # This endpoint is a simple passthrough for the widget to communicate conversationally.
    # It expects a JSON body with keys: messages (list of message objects), optional tools param.
    body = request.get_json(force=True, silent=True) or {}
    messages = body.get("messages")
    tools = body.get("tools", None)

    if messages is None:
        return jsonify({"error": "missing messages field"}), 400

    # call the same call_gpt function from hotel_agent, preserving behavior
    try:
        ai_msg = hotel_agent.call_gpt(messages, tools=tools)
        # ai_msg may be a complex object from the OpenAI client - convert to serializable structure
        # We will return the assistant message as text and function_call raw content if present.
        response = {
            "content": getattr(ai_msg, "content", None),
            "function_call": getattr(ai_msg, "function_call", None)
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": "internal_error", "details": str(e)}), 500

if __name__ == "__main__":
    # For local testing only. In production use Gunicorn as per Procfile.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
