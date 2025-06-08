from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Need a hand? 🖐️\n"
    "Here's what I can do (for now):\n"
    "/start - Greet ya like a boss\n"
    "/help - Show this awesome guide\n"
    "\n📎 Drop a CSV or XLSX file - I’ll sniff through it like a truffle pig 🐷📊\n"
    "\nMore cool stuff coming soon 🤘"
    )

def help_command():
    return CommandHandler("help", help)
