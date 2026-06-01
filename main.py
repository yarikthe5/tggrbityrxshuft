import os

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from db import *

TOKEN = os.getenv("BOT_TOKEN")

REQUEST_TOPIC_ID = 123
SCHEDULE_TOPIC_ID = 124


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт 👋\n"
        "/setrole бар\n"
        "/off 2026-06-05\n"
        "/schedule"
    )


async def setrole(update: Update, context):
    role = " ".join(context.args)

    uid = update.effective_user.id
    name = update.effective_user.first_name

    set_user(uid, name, role)

    await update.message.reply_text(
        f"✅ Роль встановлена: {role}"
    )


async def off(update: Update, context):
    if not context.args:
        await update.message.reply_text(
            "Приклад: /off 2026-06-05"
        )
        return

    day = context.args[0]

    uid = update.effective_user.id
    name = update.effective_user.first_name

    c = conn()
    cur = c.cursor()

    cur.execute(
        "SELECT role FROM users WHERE telegram_id=?",
        (uid,),
    )

    row = cur.fetchone()
    c.close()

    if not row:
        await update.message.reply_text(
            "Спочатку /setrole"
        )
        return

    role = row[0]

    req_id = add_request(day, uid, name, role)

    keyboard = [[
        InlineKeyboardButton(
            "✅ Прийняти",
            callback_data=f"accept:{req_id}"
        )
    ]]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        message_thread_id=REQUEST_TOPIC_ID,
        text=(
            f"🗓 Запит на вихідний\n\n"
            f"👤 {name}\n"
            f"🛠 {role}\n"
            f"📅 {day}\n\n"
            f"Хто може замінити?"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def accept(update: Update, context):
    query = update.callback_query
    await query.answer()

    req_id = int(query.data.split(":")[1])

    user = query.from_user

    row = get_pending(req_id)

    if not row:
        return

    day, requester_name, role, status = row

    if status != "pending":
        await query.edit_message_text(
            "Вже прийнято"
        )
        return

    accept_request(req_id, user.id)

    await query.edit_message_text(
        (
            f"✅ {user.first_name} бере зміну\n\n"
            f"👤 {requester_name}\n"
            f"🛠 {role}\n"
            f"📅 {day}"
        )
    )


async def schedule(update: Update, context):
    rows = get_schedule()

    text = "📅 Графік\n\n"

    if not rows:
        text += "Поки порожньо"

    for day, uid, role in rows:
        text += f"{day} — {role}\n"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        message_thread_id=SCHEDULE_TOPIC_ID,
        text=text
    )


def main():
    if not TOKEN:
        raise Exception("BOT_TOKEN missing")

    init_db()

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setrole", setrole))
    app.add_handler(CommandHandler("off", off))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CallbackQueryHandler(accept))

    app.run_polling()


if __name__ == "__main__":
    main()
