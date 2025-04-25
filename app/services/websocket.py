import json
import requests

RENDER_WS_URL = 'https://websocket-on-render.com/api/notify'  # لینک REST API روی WebSocket Render

def notify_user(user_id, new_balance):
    payload = {
        "userId": user_id,
        "newBalance": new_balance
    }
    try:
        requests.post(RENDER_WS_URL, json=payload)
    except Exception as e:
        print(f"Error sending update to websocket server: {e}")
