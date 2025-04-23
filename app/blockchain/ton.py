import json
from tonclient.client import TonClient
from tonclient.types import ParamsOfEncodeMessage, Abi
from app.core.app_core_config import Config  # ایمپورت تنظیمات


class TonProcessor:
    def __init__(self):
        self.client = TonClient(
            config={
                "network": {
                    "server_address": Config.TON_RPC_URL,
                    "api_key": Config.TON_API_KEY,
                }
            }
        )
        with open(Config.TON_ABI_PATH, "r") as f:
            self.contract_abi = Abi.from_json(json.load(f))
        self.contract_address = Config.TON_CONTRACT_ADDRESS

    def create_message(self, receiver, amount):
        # ایجاد پیام برای فراخوانی تابع انتقال در قرارداد
        return {
            "address": self.contract_address,
            "function_name": "transfer",
            "input": {"to": receiver, "amount": amount},
        }

    def transfer(self, receiver, amount):
        message = self.create_message(receiver, amount)
        params = ParamsOfEncodeMessage(message=message, abi=self.contract_abi)
        encoded_message = self.client.abi.encode_message(params)
        result = self.client.network.send_message(params=encoded_message)
        return result["transaction"]["id"]

    def check_transaction(self, tx_hash):
        # پیاده‌سازی نمونه جهت بررسی تراکنش (بایستی بر اساس نیاز واقعی توسعه یابد)
        # این متد باید وضعیت تراکنش را از بلاکچین دریافت کند
        return True  # فرض می‌کنیم تراکنش موفق بوده است
