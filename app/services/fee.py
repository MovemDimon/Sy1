import requests
from app.core.config import Config


class FeeService:
    @staticmethod
    def get_fee():
        """
        دریافت نرخ گس (Gas Price) از API خارجی یا مقدار پیش‌فرض.
        """
        try:
            resp = requests.get(Config.GAS_API_URL, timeout=5)
            resp.raise_for_status()
            return resp.json().get("fast", Config.DEFAULT_FEE)
        except Exception:
            return Config.DEFAULT_FEE
