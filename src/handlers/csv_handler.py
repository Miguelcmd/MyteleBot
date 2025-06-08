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
        #headers = df.columns.tolist()
        #headers_text = "\n".join(f"🔹 {col}" for col in headers)

                
        if len(df) > 0:
            first_row = df.iloc[0].to_dict()
            first_row_text = "\n".join([f"*{k}*: {v}" for k, v in first_row.items()])
            combined_text = f"🧠 *It’s all right here, dude!*\n{first_row_text}"
        else:
            combined_text = "😶 File’s empty bro... nada que ver." 


        rows, cols = df.shape

        # Reacción especial si es un archivo grande
        chunky_reaction = ""
        if rows > 1000 or cols > 20:
            chunky_reaction = (
                f"\n\n🧱 Whoa, that's a *chunky file*, dude! 📂💪\n"
                f"It has `{rows}` rows and `{cols}` columns. 🍔📊"
            )


        # Duplicados por columna
            duplicates_info = "\n".join([
        f"{i + 1}. *{col}*: {df[col].duplicated().sum()}"
        for i, col in enumerate(df.columns)
    ])


        await status_msg.edit_text(
            f"{combined_text}\n\n"
            f"🔁 *Repeated Values per Column:*\n{duplicates_info}"
            f"{chunky_reaction}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"💥 Uh-oh! Something went wrong: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def csv_file_handler():
    # Acepta tanto CSV como XLSX
    return MessageHandler(
        filters.Document.MimeType("text/csv") | filters.Document.MimeType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        analyze_csv
    )
