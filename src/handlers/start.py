from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"Hey fella 👋 What's up, {user}? I'm ready to roll.\n"
        f"Type /help if you're lost in the sauce 🧭"
    )

def start_command():
    return CommandHandler("start", start)