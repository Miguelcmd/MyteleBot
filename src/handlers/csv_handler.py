from telegram import Update, Document, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.helpers import escape_markdown
import pandas as pd
import os

TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# 🧠 Función principal que analiza el CSV/XLSX
async def analyze_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document: Document = update.message.document
    file_name = document.file_name.lower()
    
    if not (file_name.endswith('.csv') or file_name.endswith('.xlsx')):
        await update.message.reply_text("🌀 Sorry dude, I can only vibe with CSV and XLSX files right now.")
        return
    
    status_msg = await update.message.reply_text("🧠 Hang tight, I'm checking your file...")

    file = await document.get_file()
    file_path = os.path.join(TEMP_FOLDER, file_name)
    await file.download_to_drive(file_path)

    try:
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        if len(df) > 0:
            first_row = df.iloc[0].to_dict()
            first_row_text = "\n".join([f"*{k}*: {v}" for k, v in first_row.items()])
            combined_text = f"🧠 *It’s all right here, dude!*\n{first_row_text}"
        else:
            combined_text = "😶 File’s empty bro... nada que ver." 

        rows, cols = df.shape

        chunky_reaction = ""
        if rows > 1000 or cols > 20:
            chunky_reaction = (
                f"\n\n🧱 Whoa, that's a *chunky file*, dude! 📂💪\n"
                f"It has `{rows}` rows and `{cols}` columns. 🍔📊"
            )

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

        # 🔎 Ahora detectar duplicados EXACTOS
        total_duplicates = df[df.duplicated()]
        print(f"Total duplicates found: {len(total_duplicates)}")
        if not total_duplicates.empty:
            sample_dupes = escape_markdown(total_duplicates.head(2).to_string(index=False), version=2)
            # Guardamos los datos en contexto
            context.user_data["df"] = df
            context.user_data["file_name"] = file_name

            keyboard = [
                [
                    InlineKeyboardButton("✅ Yes", callback_data="delete_duplicates_yes"),
                    InlineKeyboardButton("❌ No", callback_data="delete_duplicates_no")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"🔁 Yo! Found `{len(total_duplicates)}` rows that are *totally identical*.\n"
                f"Here’s a sneak peek:\n```\n{sample_dupes}\n```\n"
                "Want me to erase those clones?",
                parse_mode="MarkdownV2",
                reply_markup=reply_markup
            )

    except Exception as e:
        await update.message.reply_text(f"💥 Uh-oh! Something went wrong: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ✅ Función para manejar respuesta de los botones
async def handle_duplicate_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    df = context.user_data.get("df")
    file_name = context.user_data.get("file_name")

    if not df or not file_name:
        await query.edit_message_text("😕 Sorry dude, I lost your data.")
        return

    if query.data == "delete_duplicates_yes":
        df_clean = df.drop_duplicates()
        clean_path = os.path.join(TEMP_FOLDER, f"cleaned_{file_name}")

        if file_name.endswith(".csv"):
            df_clean.to_csv(clean_path, index=False)
        else:
            df_clean.to_excel(clean_path, index=False)

        rows, cols = df_clean.shape

        await query.edit_message_text(
            f"🧼 Done! Removed duplicates.\nNow you've got `{rows}` rows and `{cols}` columns."
        )
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=open(clean_path, "rb"),
            filename=f"cleaned_{file_name}"
        )

    elif query.data == "delete_duplicates_no":
        await query.edit_message_text("😎 Alright, keeping the clones. No changes made.")


# 👉 Exportar handler
def csv_file_handler():
    return MessageHandler(
        filters.Document.MimeType("text/csv") | filters.Document.MimeType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        analyze_csv
    )

def duplicate_callback_handler():
    return CallbackQueryHandler(handle_duplicate_response, pattern="delete_duplicates_.*")
