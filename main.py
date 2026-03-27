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
        return True
    except:
        return False

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

    if username in monitoring:
        await update.message.reply_text(f"⚠️ Already monitoring {username}")
        return

    active = is_active(username)

    if active:
        await update.message.reply_text(f"✅ {username} is active")
    else:
        monitoring[username] = {
            "chat_id": chat_id,
            "last_status": False,
            "start_time": time.time()
        }
        await update.message.reply_text(f"👀 Monitoring started for {username}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /stop username")
        return

    username = context.args[0]

    if username in monitoring:
        del monitoring[username]
        await update.message.reply_text(f"🛑 Stopped monitoring {username}")
    else:
        await update.message.reply_text(f"❌ {username} not monitored")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not monitoring:
        await update.message.reply_text("📭 No usernames monitored")
        return

    msg = "📋 Monitoring list:\n"
    for user in monitoring:
        msg += f"- {user}\n"

    await update.message.reply_text(msg)

async def monitor_loop(app):
    while True:
        for username in list(monitoring.keys()):
            data = monitoring[username]
            current = is_active(username)

            if current and not data["last_status"]:
                elapsed = int(time.time() - data["start_time"])
                await app.bot.send_message(
                    data["chat_id"],
                    f"🔥 {username} is ACTIVE!\n⏱ {format_time(elapsed)}"
                )
                data["last_status"] = True

            elif not current and data["last_status"]:
                await app.bot.send_message(
                    data["chat_id"],
                    f"❌ {username} became INACTIVE"
                )
                data["last_status"] = False
                data["start_time"] = time.time()

        await asyncio.sleep(30)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("list", list_users))

async def start_monitor(app):
    asyncio.create_task(monitor_loop(app))

app.post_init = start_monitor

print("Dexthcrawl Monitor Running...")
app.run_polling()
