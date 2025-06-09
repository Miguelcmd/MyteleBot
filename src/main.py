import os
from dotenv import load_dotenv
from telegram.ext import Application
from src.handlers.start import start_command
from src.handlers.help import help_command
from src.handlers.joke_handler import joke_command_handler
from src.handlers.csv_handler import csv_file_handler, duplicate_callback_handler


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(csv_file_handler())
    app.add_handler(duplicate_callback_handler())
    app.add_handler(joke_command_handler())
    app.add_handler(start_command())
    app.add_handler(help_command())
    print("🤖 Bot running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
    
    
   