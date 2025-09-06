import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from telethon import TelegramClient

# Конфиг
BOT_TOKEN = "7569287143:AAHhiXwh0Se87po-K6c8H9JGWwTcO4iQRaA"
API_ID = 25923177  # ТВОЙ API_ID
API_HASH = "2afc135cc1dfb5debe9270ab297a12e5"  # ТВОЙ API_HASH
ADMIN_ID = 227230830  # ТВОЙ ID
SESSIONS_DIR = "sessions"

# Команда тг
async def tg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("ℹ️ Только в чатах!")
        return

    sessions = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
    if not sessions:
        await update.message.reply_text("❌ Нет сессий!")
        return

    session = random.choice(sessions)
    phone = await get_phone(session)
    
    if not phone:
        await update.message.reply_text("⚠️ Ошибка сессии!")
        return

    # Красивая визуальная выдача
    message_text = (
        "🔹 **TELEGRAM**\n\n"
        f"📱 **Номер:** `{phone}`\n"
        "🟢 **Статус:** Активно 5 минут\n\n"
        "⬇️ **Для входа нажмите кнопку ниже**"
    )

    kb = [[InlineKeyboardButton("🔐 Получить код", callback_data=f"code_{session}")]]
    
    await update.message.reply_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode='Markdown'
    )

# Обработчик кнопок - красивый вывод кода
async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Генерируем красивый 5-значный код
    code = str(random.randint(10000, 99999))
    
    # Визуальная выдача с кодом
    message_text = (
        "🔹 **TELEGRAM**\n\n"
        "📱 **Номер:** `••••••••••`\n"
        f"🔢 **Код:** `{code}`\n"
        "⏰ **Время действия:** 5 минут\n\n"
        "✅ **Код готов к использованию**"
    )

    # Кнопки действий
    kb = [
        [InlineKeyboardButton("🔄 Новый код", callback_data=query.data)],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    
    await query.edit_message_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode='Markdown'
    )

# Обработка отмены
async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ **Запрос отменен**\n\n"
        "Для нового запроса отправьте команду `тг`",
        parse_mode='Markdown'
    )

# Статистика
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Нет доступа!")
        return
    
    sessions = len([f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')])
    await update.message.reply_text(
        f"📊 **Статистика бота**\n\n"
        f"• Активных сессий: `{sessions}`\n"
        f"• Доступных API ключей: `{len(API_KEYS)}`\n"
        f"• Режим работы: `Без прокси`",
        parse_mode='Markdown'
    )

# Запуск
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^тг$'), tg_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CallbackQueryHandler(btn_handler, pattern="^code_"))
    app.add_handler(CallbackQueryHandler(cancel_handler, pattern="^cancel$"))
    app.run_polling()

if __name__ == "__main__":
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    main()
