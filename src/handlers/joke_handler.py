import httpx
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://official-joke-api.appspot.com/random_joke"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            joke = response.json()

        setup = joke.get("setup", "I got nothin’...")
        punchline = joke.get("punchline", "Well, that’s awkward.")

        await update.message.reply_text(f"😄 {setup}\n\n🤣 {punchline}")

    except Exception as e:
        await update.message.reply_text("😕 Oops! Can't reach the joke realm right now.")
        print(f"Joke API error: {e}")

def joke_command_handler():
    return CommandHandler("joke", joke)
