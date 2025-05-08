import hmac
import hashlib
from app.core.config import Config

class SignatureService:
    @staticmethod
    def sign(transaction_id, destination, amount, fee):
        """
        امضای دیجیتال تراکنش با HMAC-SHA256.
        """
        msg = f"{transaction_id}:{destination}:{amount}:{fee}"
        return hmac.new(
            Config.SECRET_KEY.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_callback(data):
        """
        اعتبارسنجی امضای callback دریافتی.
        """
        sig     = data.get('signature')
        msg     = f"{data.get('transaction_id')}:{data.get('status')}"
        expected= hmac.new(
            Config.SECRET_KEY.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(sig, expected)
