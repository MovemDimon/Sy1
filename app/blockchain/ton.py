import json
from tonclient.client import TonClient
from tonclient.types import ParamsOfEncodeMessage, Abi, ParamsOfSendMessage, ParamsOfWaitForTransaction
from app.core.config import Config  # از فایل config.py

class TonProcessor:
    def __init__(self):
        # مقداردهی TonClient با تنظیمات شبکه و کلید API
        self.client = TonClient(
            config={
                "network": {
                    "server_address": Config.TON_RPC_URL,
                    "api_key":        Config.TON_API_KEY,
                }
            }
        )
        # بارگذاری ABI قرارداد از فایل JSON
        with open(Config.TON_ABI_PATH, "r") as f:
            self.contract_abi = Abi.from_json(json.load(f))
        self.contract_address = Config.TON_CONTRACT_ADDRESS

    def create_message(self, receiver: str, amount: int) -> dict:
        """
        ساختار پیام برای فراخوانی تابع transfer در قرارداد.
        """
        return {
            "address":       self.contract_address,
            "function_name": "transfer",
            "input": {
                "to":     receiver,
                "amount": str(amount)  # برخی قراردادها مقدار را به صورت رشته انتظار دارند
            }
        }

    def send_transaction(self, transaction_id: str, destination: str, amount: int, fee: int, signature: str) -> str:
        """
        ارسال تراکنش به شبکه TON:
        - امضای داده‌ها در لایهٔ بالاتر ایجاد شده و اینجا تنها payload اصلی قرارداد ارسال می‌شود.
        - برای گس‌پرایس و کارمزد، می‌توانید این مقادیر را در config نود تنظیم کنید یا به پارامترهای client اضافه کنید.
        """
        # ساخت پیام قرارداد
        msg = self.create_message(destination, amount)
        # encode کردن پیام
        encode_params = ParamsOfEncodeMessage(
            abi=            self.contract_abi,
            signer=None,  # چون قرارداد از کلید خودکار استفاده می‌کند
            address=None,
            deploy_set=None,
            call_set=msg
        )
        encoded = self.client.abi.encode_message(params=encode_params)
        # ارسال پیام
        send_params = ParamsOfSendMessage(
            message=encoded.message,
            send_events=False
        )
        result = self.client.net.send_message(params=send_params)
        # می‌توانیم منتظر تایید اولیه هم بمانیم
        wait_params = ParamsOfWaitForTransaction(
            abi=            self.contract_abi,
            message=        encoded.message,
            shard_block_id=None,
            send_events=False
        )
        tx = self.client.net.wait_for_transaction(params=wait_params)
        # بازگرداندن شناسه تراکنش
        return tx.transaction.id

    def check_transaction(self, tx_hash: str) -> bool:
        """
        بررسی وضعیت تراکنش در شبکه TON.
        می‌توانید با استفاده از wait_for_transaction یا متدهای query وضعیت نهایی را بخوانید.
        """
        try:
            params = ParamsOfWaitForTransaction(
                abi=            self.contract_abi,
                message=        None,
                shard_block_id=None,
                send_events=False,
                wait_timeout=30_000  # میلی‌ثانیه
            )
            # اگر تراکنش با tx_hash در بلاک‌چین پیدا شود، موفقیت‌آمیز است
            self.client.net.wait_for_transaction(params={**params, "transaction_id": tx_hash})
            return True
        except Exception:
            return False
