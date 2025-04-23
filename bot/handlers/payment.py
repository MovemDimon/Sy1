from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import requests
import json
import base64
from app.core.app_core_config import Config  # ایمپورت تنظیمات

# مراحل مکالمه
CURRENCY, NETWORK, WALLET = range(3)


def start_payment(update: Update, context: CallbackContext) -> int:
    deeplink_data = context.args[0] if context.args else None
    if deeplink_data and deeplink_data.startswith("pay_"):
        encoded_data = deeplink_data.split("_")[1]
        decoded_data = json.loads(base64.b64decode(encoded_data).decode())
        context.user_data["package"] = decoded_data

    # نمایش انتخاب ارز
    keyboard = [
        [InlineKeyboardButton("USDT", callback_data="USDT")],
        [InlineKeyboardButton("TON", callback_data="TON")],
    ]
    update.message.reply_text(
        "🔹 لطفا ارز مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CURRENCY


def select_network(update: Update, context: CallbackContext) -> int:
    context.user_data["currency"] = update.callback_query.data
    networks = (
        ["Ethereum", "BSC", "TON"]
        if context.user_data["currency"] == "USDT"
        else ["TON"]
    )

    keyboard = [[InlineKeyboardButton(n, callback_data=n) for n in networks]]
    update.callback_query.edit_message_text(
        f'🌐 شبکه مورد نظر برای {context.user_data["currency"]} را انتخاب کنید:',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return NETWORK


def get_wallet(update: Update, context: CallbackContext) -> int:
    context.user_data["network"] = update.callback_query.data
    update.callback_query.edit_message_text("📨 لطفا آدرس کیف پول خود را وارد کنید:")
    return WALLET


def process_payment(update: Update, context: CallbackContext) -> int:
    context.user_data["wallet"] = update.message.text

    # ارسال درخواست به سرور
    response = requests.post(
        "https://daimonium.ir/api/v1/process-payment",
        headers={"Authorization": f"Bearer {Config.TELEGRAM_BOT_TOKEN}"},
        json={
            "user_id": context.user_data["package"]["userId"],
            "amount": context.user_data["package"]["usdPrice"],
            **context.user_data,
        },
    )

    if response.status_code == 202:
        update.message.reply_text(
            f'✅ تراکنش شما با شناسه {response.json()["tx_hash"]} ثبت شد!'
        )
    else:
        update.message.reply_text("❌ خطا در پردازش پرداخت!")

    return ConversationHandler.END
