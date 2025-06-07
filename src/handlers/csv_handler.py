from telegram import Update, Document
from telegram.ext import MessageHandler, filters, ContextTypes
import pandas as pd
import os

async def analyze_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document: Document = update.message.document

    if not document.file_name.endswith('.csv'):
        await update.message.reply_text("😅 Solo acepto archivos CSV por ahora.")
        return

    file = await document.get_file()
    file_path = f"/tmp/{document.file_name}"
    await file.download_to_drive(file_path)

    try:
        df = pd.read_csv(file_path)

        # Cabeceras
        headers = df.columns.tolist()
        headers_text = "\n".join(f"🔹 {col}" for col in headers)

        # Primera fila (si existe)
        if len(df) > 0:
            first_row = df.iloc[0].to_dict()
            first_row_text = "\n".join([f"🔸 {k}: {v}" for k, v in first_row.items()])
        else:
            first_row_text = "❗ No hay datos en este archivo."

        # Duplicados por columna
        duplicates_info = "\n".join([
            f"📊 {col}: {df[col].duplicated().sum()} repetidos"
            for col in df.columns
        ])

        await update.message.reply_text(
            f"📄 *Cabeceras del CSV:*\n{headers_text}\n\n"
            f"🧪 *Primera fila:*\n{first_row_text}\n\n"
            f"🔁 *Valores repetidos por columna:*\n{duplicates_info}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"😎 Sorry dude, I can't read that file. Try sending me a CSV, yeah? {e}")
    finally:
        os.remove(file_path)

def csv_file_handler():
    return MessageHandler(filters.Document.MimeType("text/csv"), analyze_csv)
