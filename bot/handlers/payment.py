from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import json
import base64
import asyncio
import websockets

# WebSocket تنظیمات
WS_URL = "wss://your-websocket-server.com"

# مراحل مکالمه
CURRENCY, NETWORK, WALLET = range(3)

async def send_via_websocket(data: dict):
    async with websockets.connect(WS_URL) as websocket:
        await websocket.send(json.dumps(data))
        response = await websocket.recv()
        return json.loads(response)

def start_payment(update: Update, context: CallbackContext) -> int:
    deeplink_data = context.args[0] if context.args else None
    if deeplink_data and deeplink_data.startswith("pay_"):
        encoded_data = deeplink_data.split("_")[1]
        decoded_data = json.loads(base64.b64decode(encoded_data).decode())
        context.user_data["package"] = decoded_data

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

    payload = {
        "action": "start_payment",
        "user_id": context.user_data["package"]["userId"],
        "amount": context.user_data["package"]["usdPrice"],
        "currency": context.user_data["currency"],
        "network": context.user_data["network"],
        "wallet": context.user_data["wallet"],
    }

    asyncio.create_task(handle_ws(update, payload))

    update.message.reply_text(
        "⏳ در حال پردازش پرداخت شما هستیم... لطفاً شکیبا باشید."
    )

    return ConversationHandler.END

async def handle_ws(update: Update, payload: dict):
    try:
        response = await send_via_websocket(payload)
        if response.get("status") == "success":
            await update.message.reply_text(
                f'✅ تراکنش شما با شناسه {response["tx_hash"]} ثبت شد!'
            )
        else:
            await update.message.reply_text("❌ خطا در پردازش پرداخت!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطای اتصال: {str(e)}")
