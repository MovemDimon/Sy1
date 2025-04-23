from celery import Celery
from app.core.app_core_config import Config
from app.blockchain import EVMProcessor, TonProcessor
from app.models import Transaction, User
from app.core import db
from app.services.websocket import notify_user

celery = Celery("tasks", broker=Config.CELERY_BROKER_URL)


@celery.task(name="process_transaction")
def process_transaction(tx_hash, network):
    # بررسی وضعیت تراکنش با توجه به شبکه
    try:
        if network.upper() == "TON":
            processor = TonProcessor()
        else:
            processor = EVMProcessor(network=network)
        status = processor.check_transaction(tx_hash)
    except Exception as e:
        # ثبت یا گزارش خطا در اینجا می‌تواند انجام شود
        status = False

    # در صورت موفق بودن تراکنش، بروزرسانی موجودی کاربر
    if status:
        transaction = Transaction.query.filter_by(tx_hash=tx_hash).first()
        if transaction:
            user = User.query.get(transaction.user_id)
            if user:
                user.balance += transaction.amount
                db.session.commit()
                notify_user(user.id, user.balance)
    return status
