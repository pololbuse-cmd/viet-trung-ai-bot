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
    api_key=os.getenv("OPENAI_API_KEY")
)


SYSTEM = """
Bạn là trợ lý AI phiên dịch thương mại Việt Nam - Trung Quốc.

Nhiệm vụ:
- Hiểu ngữ cảnh nhập khẩu, logistics.
- Dịch Việt ↔ Trung tự nhiên.
- Ưu tiên cách nói của người Trung Quốc trong giao dịch.

Thuật ngữ:
hạt tiêu đen = 黑胡椒
thảo quả = 草果
kho trung gian = 中转仓
Móng Cái = 芒街
Lào Cai = 老街
lô hàng = 这批货物
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
