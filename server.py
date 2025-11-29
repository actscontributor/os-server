from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# ================= CONFIG =================
TOKEN = "8436214196:AAHqP58rX7vGsBlDApI4K5dNPvT0SM0L_Dg"
CHAT_ID = "8514279115"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
LOG_FILE = "logs.txt"
# ==========================================


def log_data(data):
    """Write logs to file"""
    with open(LOG_FILE, "a") as f:
        f.write(data + "\n")


def send_telegram(msg):
    """Send message to Telegram"""
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    requests.post(TELEGRAM_URL, json=payload)


@app.route("/", methods=["GET", "POST"])
def catch_requests():

    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # IP Info
    client_ip = request.headers.get('CF-Connecting-IP') or request.remote_addr

    # Method & Path
    method = request.method
    path = request.path

    # Body
    try:
        body = request.get_json(force=True, silent=True)
        body_text = json.dumps(body, indent=2) if body else "❌ No JSON Body"
    except:
        body_text = "❌ Failed to parse JSON body"

    # Headers
    headers = json.dumps(dict(request.headers), indent=2)

    log_entry = f"""
======= NEW REQUEST =======
⏱ Time: {time_stamp}
🌍 IP: {client_ip}
🔹 Method: {method}
📍 Path: {path}

📦 Body:
{body_text}

📨 Headers:
{headers}
============================
"""

    log_data(log_entry)

    # Telegram message (simplified)
    telegram_msg = f"""
🚨 *Request Received!*
🌍 *IP:* `{client_ip}`
🔹 *Method:* `{method}`
📍 *Path:* `{path}`

📦 *Body Preview:* `{body_text[:150]}`
"""

    send_telegram(telegram_msg)

    return jsonify({"status": "logged"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Server running on port {port}")
    app.run(host="0.0.0.0", port=port)

