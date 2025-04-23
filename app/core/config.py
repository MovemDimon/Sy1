import os


class Config:
    FLASK_SECRET = os.getenv("FLASK_SECRET")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ETH_RPC_URL = os.getenv("ETH_RPC_URL")
    BSC_RPC_URL = os.getenv("BSC_RPC_URL")
    TON_RPC_URL = os.getenv("TON_RPC_URL")
    TON_API_KEY = os.getenv("TON_API_KEY")
    USDT_ETH_CONTRACT = os.getenv("USDT_ETH_CONTRACT")
    USDT_TON_CONTRACT = os.getenv("USDT_TON_CONTRACT")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")

    # کیف پول‌های مقصد ثابت
    TON_MERCHANT_WALLET = os.getenv("TON_MERCHANT_WALLET")
    ETH_MERCHANT_WALLET = os.getenv("ETH_MERCHANT_WALLET")

    # دیکشنری آدرس قراردادها
    CONTRACT_ADDRESSES = {
        "USDT": os.getenv("USDT_ETH_CONTRACT"),
        # در صورت نیاز ارزهای دیگر هم اضافه کنید.
    }
