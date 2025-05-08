import json
import base64
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
import websockets
from app.core.config import Config
from app.core.config import Config
from telegram.ext import CallbackContext, MessageHandler, Filters, CallbackQueryHandler
import requests

# استفاده از URL وب‌سوکت از تنظیمات محیطی
WS_URL = Config.WS_URL

# مراحل مکالمه
CURRENCY, NETWORK, WALLET, CONFIRM = range(4)


async def send_via_websocket(data: dict) -> dict:
    """
    ارسال payload به WebSocket و دریافت پاسخ.
    """
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps(data))
        resp = await ws.recv()
        return json.loads(resp)


def start_payment(update: Update, context: CallbackContext) -> int:
    args = context.args or []
    if args and args[0].startswith("pay_"):
        encoded = args[0].split("_", 1)[1]
        decoded = json.loads(base64.b64decode(encoded).decode())
        context.user_data["package"] = decoded
    else:
        update.message.reply_text("خطا: بسته پرداخت یافت نشد.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("USDT", callback_data="USDT")],
        [InlineKeyboardButton("TON", callback_data="TON")],
    ]
    update.message.reply_text(
        "🔹 لطفاً ارز مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CURRENCY


def select_network(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    context.user_data["currency"] = query.data
    networks = ["Ethereum", "BSC", "TON"] if query.data == "USDT" else ["TON"]
    keyboard = [[InlineKeyboardButton(n, callback_data=n)] for n in networks]
    query.edit_message_text(
        f"🌐 شبکه مورد نظر برای {query.data} را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return NETWORK


def ask_wallet(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    context.user_data["network"] = query.data
    query.edit_message_text("📨 لطفاً آدرس کیف پول مقصد را وارد کنید:")
    return WALLET


def confirm_payment(update: Update, context: CallbackContext) -> int:
    wallet = update.message.text.strip()
    context.user_data["wallet"] = wallet

    # ابتدا payload را به WebSocket می‌فرستیم تا داده‌های لازم را دریافت کنیم
    payload_ws = {
        "action": "prepare_payment",
        "package": context.user_data["package"],
        "currency": context.user_data["currency"],
        "network": context.user_data["network"],
        "wallet": wallet,
    }
    # اجرای ارتباط WebSocket در پس‌زمینه
    asyncio.create_task(_handle_ws_and_ask_confirmation(update, context, payload_ws))
    update.message.reply_text("⏳ در حال آماده‌سازی پرداخت… لطفاً صبر کنید.")
    return ConversationHandler.END  # تا دیالوگ ادامه نیابد


async def _handle_ws_and_ask_confirmation(
    update: Update, context: CallbackContext, payload_ws: dict
):
    try:
        # دریافت داده‌های amount, fee, transaction_id از WebSocket
        resp = await send_via_websocket(payload_ws)
        if resp.get("status") != "ready":
            await update.message.reply_text("❌ خطا در دریافت اطلاعات پرداخت!")
            return

        # ساخت کی‌بورد تأیید
        amount = resp["amount"]
        fee = resp["fee"]
        tx_id = resp["transaction_id"]
        package_name = context.user_data["package"]["name"]

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✅ بله", callback_data=f"confirm_ws:{tx_id}"),
                    InlineKeyboardButton("❌ لغو", callback_data=f"cancel_ws:{tx_id}"),
                ]
            ]
        )
        await update.message.reply_text(
            f"بسته: {package_name} — مبلغ: {amount} {context.user_data['currency']}\n"
            f"کارمزد: {fee}\n"
            f"آدرس مقصد: {context.user_data['wallet']}\n\n"
            "آیا مایل به ادامه تراکنش هستید؟",
            reply_markup=keyboard,
        )
    except Exception as e:
        await update.message.reply_text(f"❌ خطای WebSocket: {str(e)}")


def execute_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    action, tx_id = query.data.split(":", 1)

    if action == "confirm_ws":
        # پس از تأیید، درخواست REST برای نهایی‌سازی تراکنش
        resp = requests.post(
            f"{Config.API_URL}/api/v1/payments/execute",
            json={"transaction_id": tx_id},
            headers={"Authorization": f"Bearer {context.bot_data['jwt_token']}"},
        )
        if resp.status_code == 200:
            status = resp.json().get("status", "submitted")
            query.edit_message_text(f"✅ تراکنش شما با وضعیت {status} ارسال شد.")
        else:
            query.edit_message_text("❌ خطا در ارسال نهایی تراکنش.")
    else:
        query.edit_message_text("❌ تراکنش شما لغو شد.")
    return ConversationHandler.END


# تعریف ConversationHandler
payment_conversation = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(r"^/pay"), start_payment)],
    states={
        CURRENCY: [CallbackQueryHandler(select_network)],
        NETWORK: [CallbackQueryHandler(ask_wallet)],
        WALLET: [MessageHandler(Filters.text & ~Filters.command, confirm_payment)],
        # CONFIRM handled via WebSocket callback_data "confirm_ws:" / "cancel_ws:"
        CONFIRM: [
            CallbackQueryHandler(execute_callback, pattern=r"^(confirm_ws|cancel_ws):")
        ],
    },
    fallbacks=[],
)
