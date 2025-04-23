from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.blockchain import EVMProcessor, TonProcessor
from app.services.conversion import CurrencyConverter
from app.models import Transaction
from app.core import db, Config
from app.services.celery_worker import process_transaction

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/process-payment", methods=["POST"])
@jwt_required()
def process_payment():
    data = request.get_json()
    # اعتبارسنجی ورودی
    required_fields = ["user_id", "amount", "currency", "network"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return (
            jsonify({"error": f"فیلد(های) مورد نیاز {missing_fields} موجود نیست."}),
            400,
        )

    try:
        usdt_amount = CurrencyConverter.to_usdt(data["amount"], data["currency"])
    except Exception as e:
        return jsonify({"error": f"خطا در تبدیل ارز: {str(e)}"}), 400

    try:
        if data["network"].upper() == "TON":
            processor = TonProcessor()
            # انتقال پرداخت به آدرس ثابت تون (کیف پول مقصد)
            tx_hash = processor.transfer(Config.TON_MERCHANT_WALLET, usdt_amount)
        else:
            processor = EVMProcessor(network=data["network"])
            # انتقال پرداخت به آدرس ثابت متامسک (کیف پول مقصد در شبکه EVM)
            tx_hash = processor.transfer_erc20(
                Config.ETH_MERCHANT_WALLET,
                usdt_amount,
                Config.CONTRACT_ADDRESSES.get(data["currency"]),
            )
    except Exception as e:
        return jsonify({"error": f"خطا در پردازش تراکنش: {str(e)}"}), 500

    # ذخیره تراکنش در دیتابیس
    transaction = Transaction(
        user_id=data["user_id"],
        tx_hash=tx_hash,
        amount=usdt_amount,
        currency=data["currency"],
        network=data["network"],
    )
    db.session.add(transaction)
    db.session.commit()

    # فراخوانی تسک ناهمزمان با Celery
    process_transaction.delay(tx_hash, data["network"])

    return jsonify({"tx_hash": tx_hash}), 202
