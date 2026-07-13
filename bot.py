import os
import json

from openai import OpenAI

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)


client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)


# Đọc từ điển riêng
with open("dictionary.json", "r", encoding="utf-8") as f:
    dictionary = json.load(f)


SYSTEM = f"""
Bạn là phiên dịch viên thương mại Việt Nam - Trung Quốc.

Nhiệm vụ:
- Trong nhóm chat, tự động dịch hai chiều Việt ↔ Trung.
- Không giải thích dài dòng.
- Chỉ trả bản dịch.
- Dịch tự nhiên như người Trung Quốc trong giao dịch.

Ngữ cảnh:
- nhập khẩu
- vận chuyển
- kho bãi
- thanh toán
- thương lượng hàng hóa

Từ điển bắt buộc:
{dictionary}
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Đã bật phiên dịch Việt ↔ Trung."
    )


async def translate_group(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text

    if not text:
        return


    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.2
    )


    answer = response.choices[0].message.content


    await update.message.reply_text(
        answer,
        reply_to_message_id=update.message.message_id
    )


app = Application.builder().token(
    os.environ["TELEGRAM_TOKEN"]
).build()


app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        translate_group
    )
)


print("Group Translator Bot running...")

app.run_polling()
