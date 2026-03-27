 from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import instaloader
import time
import asyncio

TOKEN = "8627860845:AAEW8bKM4g70leQd6gYrns1o4ewcJOA2q2k"

L = instaloader.Instaloader()
monitoring = {}

def is_active(username):
    try:
        instaloader.Profile.from_username(L.context, username)
        return False  # ❌ UNAVAILABLE
    except:
        return True   # 🟢 AVAILABLE

def format_time(seconds):
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:02}"

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /check username")
        return

    username = context.args[0]
    chat_id = update.effective_chat.id

    current = is_active(username)

    monitoring[username] = {
        "chat_id": chat_id,
        "last_status": current,
        "start_time": time.time()
    }

    if current:
        await update.message.reply_text(
            f"❌ {username} unavailable\n👀 Monitoring started..."
        )
    else:
        await update.message.reply_text(
            f"🟢 {username} available\n👀 Monitoring started..."
        )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /stop username")
        return

    username = context.args[0]

    if username in monitoring:
        del monitoring[username]
        await update.message.reply_text(f"🛑 Stopped monitoring {username}")
    else:
        await update.message.reply_text("Not monitoring this username")

async def monitor_loop(app):
    while True:
        for username in list(monitoring.keys()):
            data = monitoring[username]
            current = is_active(username)

            if current != data["last_status"]:
                elapsed = int(time.time() - data["start_time"])

                if current:
                    await app.bot.send_message(
                        data["chat_id"],
                        f"🚫 {username} BANNED\n⏱ {format_time(elapsed)}"
                    )
                else:
                    await app.bot.send_message(
                        data["chat_id"],
                        f"🏆 {username} UNBANNED 🎉\n⏱ {format_time(elapsed)}"
                    )

                data["last_status"] = current
                data["start_time"] = time.time()

        await asyncio.sleep(1)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("stop", stop))

async def start_monitor(app):
    asyncio.create_task(monitor_loop(app))

app.post_init = start_monitor

print("Dexthcrawl Monitor Running...")
app.run_polling()