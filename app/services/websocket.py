import json
import requests
import random

# لیست WebSocket Server ها (روی Fly.io یا Render یا هر جای دیگر)
WEBSOCKET_SERVERS = [
    "https://ws-server-1.fly.io/notify",
    "https://ws-server-2.fly.io/notify",
    "https://ws-server-3.fly.io/notify"
]

def notify_user(user_id, new_balance):
    payload = {
        "userId": user_id,
        "event": "balance_updated",
        "data": {"newBalance": new_balance}
    }
    try:
        selected_url = random.choice(WEBSOCKET_SERVERS)
        requests.post(selected_url, json=payload)
    except Exception as e:
        print(f"Error sending update to websocket server: {e}")
