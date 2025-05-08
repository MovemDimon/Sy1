from uuid import uuid4
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.blockchain.ton import TonProcessor
from app.services.fee import FeeService
from app.services.signature import SignatureService
from app.core import db
from app.models import Transaction, Package
from app.api.v1.notifications import send_telegram_notification

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/api/v1/payments", methods=["POST"])
@jwt_required()
def create_payment():
    data = request.get_json() or {}
    dest = data.get("destination_address")
    gateway = data.get("gateway")
    currency = data.get("currency")
    package_id = data.get("package_id")
    if not all([dest, gateway, currency, package_id]):
        abort(400, description="Missing required fields")

    pkg = Package.query.get(package_id)
    if not pkg:
        abort(404, description="Package not found")
    amount = pkg.price  # مبلغ خودکار از بسته

    # تولید شناسه تراکنش یکتا
    tx_id = str(uuid4())
    tx = Transaction(
        transaction_id=tx_id,
        user_id=get_jwt_identity(),
        destination=dest,
        gateway=gateway,
        currency=currency,
        amount=amount,
        status="pending",
    )
    db.session.add(tx)
    db.session.commit()

    # محاسبه کارمزد
    fee = FeeService.get_fee()

    # امضای دیجیتال
    signature = SignatureService.sign(
        transaction_id=tx_id, destination=dest, amount=amount, fee=fee
    )

    # ارسال تراکنش
    try:
        tx_hash = TonProcessor.send_transaction(
            transaction_id=tx_id,
            destination=dest,
            amount=amount,
            fee=fee,
            signature=signature,
        )
    except Exception as e:
        tx.status = "failed"
        db.session.commit()
        abort(502, description=str(e))

    # بروزرسانی وضعیت و ذخیره هش
    tx.tx_hash = tx_hash
    tx.status = "submitted"
    db.session.commit()

    return (
        jsonify(
            {"transaction_id": tx_id, "tx_hash": tx_hash, "amount": amount, "fee": fee}
        ),
        202,
    )


@payments_bp.route("/api/v1/payments/execute", methods=["POST"])
@jwt_required()
def execute_payment():
    data = request.get_json() or {}
    tx_id = data.get("transaction_id")
    tx = Transaction.query.filter_by(transaction_id=tx_id).first_or_404()
    if tx.status != "submitted":
        abort(400, description="Transaction not in a state to execute")
    try:
        result = TonProcessor.finalize_transaction(tx)
        tx.status = result.get("status", tx.status)
        db.session.commit()
    except Exception as e:
        abort(502, description=str(e))
    return jsonify({"status": tx.status}), 200


@payments_bp.route("/api/v1/payments/callback", methods=["POST"])
def payments_callback():
    data = request.get_json() or {}
    if not SignatureService.verify_callback(data):
        abort(401, description="Invalid signature")

    tx = Transaction.query.filter_by(
        transaction_id=data.get("transaction_id")
    ).first_or_404()
    tx.status = data.get("status")
    tx.tx_hash = data.get("tx_hash", tx.tx_hash)
    tx.confirm_count = data.get("confirm_count", tx.confirm_count)
    tx.error_message = data.get("error_message", tx.error_message)
    db.session.commit()

    send_telegram_notification(
        chat_id=tx.user_id,
        transaction_id=tx.transaction_id,
        status=tx.status,
        tx_hash=tx.tx_hash,
        confirm_count=tx.confirm_count,
        error_message=tx.error_message,
    )
    return ("", 204)
