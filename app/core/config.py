import os


class Config:
    # کلیدهای امنیتی و آدرس پایگاه‌داده
    SECRET_KEY = os.getenv("FLASK_SECRET")
    DATABASE_URL = os.getenv("DATABASE_URL")

    # RPC URLها و کلید API برای بلاک‌چین
    ETH_RPC_URL = os.getenv("ETH_RPC_URL")
    BSC_RPC_URL = os.getenv("BSC_RPC_URL")
    TON_RPC_URL = os.getenv("TON_RPC_URL")
    TON_API_KEY = os.getenv("TON_API_KEY")

    # مسیر فایل ABI و آدرس قرارداد TON
    TON_ABI_PATH = os.getenv("TON_ABI_PATH")  # مثال: "/app/abi/YourContract.json"
    TON_CONTRACT_ADDRESS = os.getenv("TON_CONTRACT_ADDRESS")  # مثال: "EQC..."

    # قراردادهای توکن‌ها روی Ethereum/Ton
    USDT_ETH_CONTRACT = os.getenv("USDT_ETH_CONTRACT")
    USDT_TON_CONTRACT = os.getenv("USDT_TON_CONTRACT")
    CONTRACT_ADDRESSES = {
        "USDT": USDT_ETH_CONTRACT,
        # در صورت نیاز ارزهای دیگر هم اضافه کنید
    }

    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_API_URL = "https://api.telegram.org"

    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")

    # کیف پول‌های مقصد ثابت (Merchant Wallets)
    TON_MERCHANT_WALLET = os.getenv("TON_MERCHANT_WALLET")
    ETH_MERCHANT_WALLET = os.getenv("ETH_MERCHANT_WALLET")

    # محاسبه کارمزد در صورت لزوم
    GAS_API_URL = os.getenv("GAS_API_URL")  # مثال: Etherscan gas tracker URL
    DEFAULT_FEE = int(os.getenv("DEFAULT_FEE", "1000000000"))

    # تنظیمات API داخلی
    API_URL = os.getenv("API_URL")  # مثال: "https://api.yourdomain.com"
