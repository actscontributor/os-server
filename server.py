from flask import Flask, request
import os
from datetime import datetime
import requests

# ====== TELEGRAM CONFIG (YOURS) ======
BOT_TOKEN = "8436214196:AAHqP58rX7vGsBlDApI4K5dNPvT0SM0L_Dg"
CHAT_ID = "8514279115"

app = Flask(__name__)

# Ensure log directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")


def log_request(req):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Use forwarded IP if behind render/cloudflare
    ip = req.headers.get("X-Forwarded-For", req.remote_addr)

    # ===== Raw HTTP Request Reconstruction =====
    request_line = f"{req.method} {req.full_path if req.query_string else req.path} HTTP/1.1"

    headers = ""
    for header, value in req.headers.items():
        headers += f"{header}: {value}\n"

    body = req.get_data(as_text=True)

    raw_full_request = (
        f"\n=====================================\n"
        f"TIME: {timestamp}\n"
        f"IP: {ip}\n\n"
        f"{request_line}\n"
        f"{headers}\n"
        f"{body}\n"
        f"=====================================\n"
    )

    # Save full formatted request to daily file
    filename = f"logs/{datetime.utcnow().strftime('%Y-%m-%d')}.log"
    with open(filename, "a") as f:
        f.write(raw_full_request)

    # Telegram notification (short version)
    short_msg = f"🚨 Request Received\nIP: {ip}\nMethod: {req.method}\nPath: {req.path}"
    tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(tg_url, data={"chat_id": CHAT_ID, "text": short_msg})
    except:
        pass

    return raw_full_request


@app.route("/", defaults={'path': ''}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def catch_all(path):
    log_request(request)
    return "OK", 200


@app.route("/logs", methods=["GET"])
def view_logs():
    """View saved logs in browser"""
    content = ""
    for filename in sorted(os.listdir("logs")):
        with open(os.path.join("logs", filename)) as f:
            content += f"\n=== {filename} ===\n" + f.read()
    return f"<pre>{content}</pre>"


@app.route("/health", methods=["GET"])
def health():
    return {"status": "running"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
