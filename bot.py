import os
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

from openai import OpenAI


client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)


import json


with open("dictionary.json", "r", encoding="utf-8") as f:
    dictionary = json.load(f)


SYSTEM = f"""
Bạn là trợ lý AI phiên dịch thương mại Việt Nam - Trung Quốc.

Yêu cầu:
- Dịch tự nhiên như người Trung Quốc giao tiếp.
- Ưu tiên ngữ cảnh nhập khẩu, logistics.
- Không dịch máy từng chữ.
- Giữ nguyên số lượng, đơn vị, tên địa điểm.

Từ điển bắt buộc:

{dictionary}
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Tôi là trợ lý AI Việt-Trung.\n"
        "Bạn có thể chat hoặc gửi nội dung cần dịch."
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role":"system",
                "content":SYSTEM
            },
            {
                "role":"user",
                "content":text
            }
        ]
    )

    answer = response.choices[0].message.content

    await update.message.reply_text(answer)


app = Application.builder().token(
    os.getenv("TELEGRAM_TOKEN")
).build()


app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(
        filters.TEXT,
        chat
    )
)


print("Bot running...")

app.run_polling()
