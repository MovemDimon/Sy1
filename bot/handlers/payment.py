import json
import asyncio
from flask import Blueprint, request, jsonify

ws_router = Blueprint("ws_router", __name__)


@ws_router.route("/ws-payment", methods=["POST"])
async def handle_payment_via_ws():
    try:
        payload = request.get_json()

        # اعتبارسنجی داده‌های ورودی
        required_fields = {
            "action",
            "user_id",
            "amount",
            "currency",
            "network",
            "wallet",
        }
        if not payload or not required_fields.issubset(payload):
            return jsonify({"status": "error", "message": "Invalid payload"}), 400

        if payload["action"] != "start_payment":
            return jsonify({"status": "error", "message": "Unsupported action"}), 400

        # اجرای منطق اصلی پرداخت
        from app.payments.processor import process_payment_request

        result = await process_payment_request(payload)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
