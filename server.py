from flask import Flask, request
import os
from datetime import datetime
import requests

# ====== TELEGRAM CONFIG (YOUR TOKEN + CHAT ID ADDED) ======
BOT_TOKEN = "8436214196:AAHqP58rX7vGsBlDApI4K5dNPvT0SM0L_Dg"
CHAT_ID = "8514279115"

app = Flask(__name__)

# Ensure logs folder exists
if not os.path.exists("logs"):
    os.makedirs("logs")


def log_request(req):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    full_request = f"""
========================================
TIME: {timestamp}
IP: {ip}
METHOD: {req.method}
PATH: {req.path}
QUERY: {req.query_string.decode()}
HEADERS:
{dict(req.headers)}

BODY:
{req.get_data(as_text=True)}
========================================
"""

    # Save to file
    filename = f"logs/{datetime.utcnow().strftime('%Y-%m-%d')}.log"
    with open(filename, "a") as f:
        f.write(full_request)

    # Send Telegram notification (short version)
    short_msg = f"🚨 Request Received\nIP: {ip}\nMethod: {req.method}\nPath: {req.path}"
    tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(tg_url, data={"chat_id": CHAT_ID, "text": short_msg})

    return full_request


@app.route("/", defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def catch_all(path):
    log_request(request)
    return "OK", 200


@app.route("/logs", methods=["GET"])
def view_logs():
    """View saved logs in browser."""
    content = ""
    for filename in sorted(os.listdir("logs")):
        with open(os.path.join("logs", filename)) as f:
            content += f"\n=== FILE: {filename} ===\n" + f.read()
    return f"<pre>{content}</pre>"


@app.route("/health", methods=["GET"])
def health():
    """Render.com health check"""
    return {"status": "running"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
