from app.core.config import Config
import requests


def send_telegram_notification(
    chat_id,
    transaction_id,
    status,
    tx_hash=None,
    confirm_count=None,
    error_message=None,
):
    """
    ارسال وضعیت تراکنش به کاربر از طریق Bot API تلگرام.
    """
    text = f"تراکنش شما #{transaction_id}\nوضعیت: {status}"
    if tx_hash:
        text += f"\nهش: {tx_hash}"
    if confirm_count is not None:
        text += f"\nتعداد تأیید: {confirm_count}"
    if error_message:
        text += f"\nخطا: {error_message}"

    payload = {"chat_id": chat_id, "text": text}
    requests.post(
        f"{Config.TELEGRAM_API_URL}/bot{Config.TELEGRAM_TOKEN}/sendMessage",
        json=payload,
    )
