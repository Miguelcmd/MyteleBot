from telegram import Update, Document
from telegram.ext import MessageHandler, filters, ContextTypes
import pandas as pd
import os

async def analyze_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document: Document = update.message.document
    file_name = document.file_name.lower()
    
    if not (file_name.endswith('.csv') or file_name.endswith('.xlsx')):
        await update.message.reply_text("🌀 Sorry dude, I can only vibe with CSV and XLSX files right now.")
        return
    
    status_msg = await update.message.reply_text("🧠 Hang tight, I'm checking your file...")

    file = await document.get_file()
    file_path = f"/tmp/{document.file_name}"
    await file.download_to_drive(file_path)

    try:
        if file_name.endswith('.csv'):
           df = pd.read_csv(file_path)
        else:
           df = pd.read_excel(file_path)

        # Cabeceras
        headers = df.columns.tolist()
        headers_text = "\n".join(f"🔹 {col}" for col in headers)

        # Primera fila (si existe)
        if len(df) > 0:
            first_row = df.iloc[0].to_dict()
            first_row_text = "\n".join([f"🔸 {k}: {v}" for k, v in first_row.items()])
        else:
            first_row_text = "😶 Whoa dude, this file's emptier than my snack stash..."
            
       # Reacción especial si es un archivo grande
    chunky_reaction = ""
       if df.shape[0] > 1000 or df.shape[1] > 20:
        chunky_reaction = "\n\n🧱 Whoa, that's a *chunky file*, dude! 📂💪"
    

        # Duplicados por columna
    duplicates_info = "\n".join([
            f"📊 {col}: {df[col].duplicated().sum()} repetidos"
            for col in df.columns])

    await update.message.reply_text(
            f"📄 *Cabeceras del CSV:*\n{headers_text}\n\n"
            f"🧪 *Primera fila:*\n{first_row_text}\n\n"
            f"🔁 *Valores repetidos por columna:*\n{duplicates_info}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"💥 Uh-oh! Something went wrong: {e}")
    finally:
    if os.path.exists(file_path):
        os.remove(file_path)

def csv_file_handler():
    return MessageHandler(filters.Document.MimeType("text/csv"), analyze_csv)
