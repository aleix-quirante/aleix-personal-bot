import os
import logging
import asyncio
import ollama
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

# --- CONFIGURACIÓN SEGURA ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUR_USER_ID = int(os.getenv("USER_ID"))
MODEL_NAME = "llama3"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)

# --- MEMORIA DEL BOT ---
user_history = {}
MAX_HISTORY = 5
SYSTEM_PROMPT = {
    'role': 'system', 
    'content': 'Eres Jarvis, el asistente de IA de Aleix. Responde SIEMPRE en español, con un tono profesional, eficiente y un toque de ingenio británico (como el Jarvis de Iron Man). Estás ejecutándote en un Mac Mini M4 local.'
}

async def check_user(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id != YOUR_USER_ID:
        logging.warning(f"Intento de acceso de ID no autorizado: {user_id}")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    user_id = update.effective_user.id
    user_history[user_id] = [] # Resetear memoria al iniciar
    await update.message.reply_text("¡Jarvis en línea, señor! Mis sistemas están operativos y ejecutándose en su Mac Mini M4. ¿En qué le puedo asistir, Aleix?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    # Inicializar historial si no existe
    if user_id not in user_history:
        user_history[user_id] = []
        
    # Añadir mensaje del usuario al historial
    user_message = update.message.text
    user_history[user_id].append({'role': 'user', 'content': user_message})
    
    # Mantener solo los últimos MAX_HISTORY*2 mensajes (ida y vuelta) para no saturar contexto
    if len(user_history[user_id]) > MAX_HISTORY * 2:
        user_history[user_id] = user_history[user_id][-(MAX_HISTORY * 2):]
    
    try:
        # Construir mensajes con el prompt del sistema + historial
        messages = [SYSTEM_PROMPT] + user_history[user_id]
        
        # Ejecutamos la llamada a Ollama en un hilo separado para no bloquear el bot
        response = await asyncio.to_thread(
            ollama.chat,
            model=MODEL_NAME,
            messages=messages
        )
        
        bot_response = response['message']['content']
        
        # Añadir respuesta del bot al historial
        user_history[user_id].append({'role': 'assistant', 'content': bot_response})
        
        await update.message.reply_text(bot_response)
    except Exception as e:
        logging.error(f"Error en Ollama: {e}")
        await update.message.reply_text("Mis disculpas, señor. Parece que mi motor cognitivo principal ha sufrido un breve fallo. Sugiero revisar los registros del sistema.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Servidor Jarvis arrancando con su nueva personalidad...")
    app.run_polling()
