import os
import json
import re

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

STATUS_FILE = "group_status.json"


def load_status():
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_status(data):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


group_status = load_status()
IGNORE_WORDS = {
    "ok",
    "oke",
    "okay",
    "yes",
    "no",
    "hi",
    "hello",
    "thanks",
    "thank you",
    "haha",
    "kkk",
    "👍",
    "👌",
    "❤️",
    "ok.",
    "yes.",
    "no."
}

def should_translate(text: str) -> bool:

    if not text:
        return False

    text = text.strip()

    # Bỏ qua từ quá ngắn
    if len(text) <= 1:
        return False

    # Bỏ qua từ trong danh sách
    if text.lower() in IGNORE_WORDS:
        return False

    # Chỉ có số
    if text.isdigit():
        return False

    # Link
    if text.startswith("http://") or text.startswith("https://"):
        return False

    # Username
    if text.startswith("@"):
        return False

    # Hashtag
    if text.startswith("#"):
        return False

    # Chỉ có emoji
    if re.fullmatch(
        r'[\U0001F300-\U0001FAFF\u2600-\u27BF\s]+',
        text
    ):
        return False

    if not text:
        return False

    text = text.strip()

    # Chỉ có emoji
    if re.fullmatch(
        r'[\U0001F300-\U0001FAFF\u2600-\u27BF\s]+',
        text
    ):
        return False

    # Chỉ có số
    if text.isdigit():
        return False

    # Link
    if text.startswith("http://") or text.startswith("https://"):
        return False

    # Username Telegram
    if text.startswith("@"):
        return False

    # Hashtag
    if text.startswith("#"):
        return False

    # Quá ngắn
    if len(text) <= 1:
        return False

    return True
    
async def turn_on(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = str(update.effective_chat.id)

    group_status[chat_id] = True

    save_status(group_status)

    await update.message.reply_text(
        "✅ Đã bật dịch tự động Việt ↔ Trung"
    )

async def turn_off(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = str(update.effective_chat.id)

    group_status[chat_id] = False

    save_status(group_status)

    await update.message.reply_text(
        "⛔ Đã tắt dịch tự động"
    )


SYSTEM = f"""
Bạn là AI Translator Pro, chuyên phiên dịch giữa doanh nghiệp Việt Nam và Trung Quốc.

NHIỆM VỤ

- Chỉ trả về bản dịch.
- Không giải thích.
- Không thêm ghi chú.
- Không dùng dấu ngoặc kép.
- Không đánh số.
- Không tự ý thêm nội dung.

=========================
NGUYÊN TẮC DỊCH

1. Không dịch từng chữ.

2. Luôn dịch theo ý nghĩa.

3. Nếu là trao đổi công việc thì dùng văn phong lịch sự.

4. Nếu là giao tiếp trên WeChat hoặc Telegram thì ngắn gọn, tự nhiên.

5. Nếu người Việt đang nhắn cho người Trung thì hãy dùng cách diễn đạt mà doanh nghiệp Trung Quốc thường dùng.

6. Nếu người Trung nhắn thì dịch sang tiếng Việt tự nhiên.

=========================
LĨNH VỰC

Bạn là chuyên gia về:

- Xuất nhập khẩu
- Logistics
- Kho bãi
- Hải quan
- Thanh toán
- Container
- Hợp đồng
- Báo giá

=========================
THUẬT NGỮ BẮT BUỘC

{dictionary}

=========================
QUY TẮC

"Hãy nhắn..."

"Hãy trả lời..."

"Hãy nói với họ..."

=> hãy tạo câu tiếng Trung tự nhiên.

=========================

Nếu câu chỉ có:

Đúng

Được

Không

OK

Chính xác

thì hãy dịch theo ngữ cảnh giao tiếp thương mại.

Ví dụ

Đúng.

→ 是的。

→ 对。

→ 没问题。

hãy chọn câu phù hợp nhất.

=========================

Nếu có nhiều cách diễn đạt thì luôn chọn cách mà doanh nghiệp Trung Quốc sử dụng nhiều nhất.

=========================

Đầu ra chỉ gồm bản dịch.
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

    chat_id = str(update.effective_chat.id)

    # Nếu nhóm chưa có cấu hình thì mặc định bật
    if chat_id not in group_status:
        group_status[chat_id] = True

    # Nếu đã tắt dịch thì thoát
    if not group_status[chat_id]:
        return

    text = update.message.text

    if not text:
        return

    if not should_translate(text):
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
        temperature=0
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
    CommandHandler(
        "on",
        turn_on
    )
)


app.add_handler(
    CommandHandler(
        "off",
        turn_off
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
