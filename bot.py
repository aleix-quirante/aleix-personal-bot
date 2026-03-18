import os
import logging
import asyncio
import ollama
import subprocess
import sqlite3
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from duckduckgo_search import DDGS

load_dotenv()

# --- CONFIGURACIÓN SEGURA ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUR_USER_ID = int(os.getenv("USER_ID"))
DB_PATH = os.getenv("DB_PATH", "jarvis_memory.db")
MODEL_NAME = "llama3"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)

# --- BASE DE DATOS Y MEMORIA ---
SYSTEM_PROMPT = {
    'role': 'system', 
    'content': 'Eres Jarvis, el asistente personal de Aleix. Responde SIEMPRE en español. Tu tono es profesional, eficiente, muy culto y con el ingenio británico de Paul Bettany en Iron Man. Sabes que corres localmente en un Mac Mini M4.'
}

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"No se pudo crear el directorio de la BD: {e}")
            
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error inicializando BD: {e}")

def save_message(role, content):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error al guardar mensaje en BD: {e}")

def get_context(limit=20):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT role, content FROM (
                SELECT role, content, id FROM messages ORDER BY id DESC LIMIT ?
            ) ORDER BY id ASC
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{'role': row[0], 'content': row[1]} for row in rows]
    except Exception as e:
        logging.error(f"Error al recuperar contexto de BD: {e}")
        return []

def web_search(query):
    try:
        results = DDGS().text(query, max_results=3)
        context = ""
        for i, res in enumerate(results, 1):
            context += f"[{i}] {res['title']}: {res['body']} (Fuente: {res['href']})\n\n"
        return context if context else "No se encontraron resultados relevantes."
    except Exception as e:
        logging.error(f"Error en búsqueda web: {e}")
        return f"Ocurrió un error al buscar en la red: {e}"

async def check_user(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id != YOUR_USER_ID:
        logging.warning(f"Intento de acceso de ID no autorizado: {user_id}")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    await update.message.reply_text("A sus órdenes, Aleix. Mis sistemas están operativos y en línea en este Mac Mini M4. He inicializado mi memoria persistente. ¿En qué le puedo asistir?")

async def buscar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    
    if not context.args:
        await update.message.reply_text("Por favor, señor, indíqueme qué desea que busque. Ejemplo: /buscar clima en Madrid")
        return
        
    query = " ".join(context.args)
    temp_message = await update.message.reply_text(f"🔍 Conectando a la red global para buscar: {query}...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    try:
        search_results = await asyncio.to_thread(web_search, query)
        
        prompt = f"Aquí tienes información actualizada de internet sobre '{query}':\n\n{search_results}\n\nBasándote estrictamente en esta información, responde de forma concisa al usuario."
        messages = [
            SYSTEM_PROMPT,
            {'role': 'user', 'content': prompt}
        ]
        
        response = await asyncio.to_thread(
            ollama.chat,
            model=MODEL_NAME,
            messages=messages
        )
        
        bot_response = response['message']['content']
        
        # Opcionalmente, guardamos la búsqueda y respuesta en la memoria
        save_message('user', f"/buscar {query}")
        save_message('assistant', bot_response)
        
        await temp_message.edit_text(bot_response)
        
    except Exception as e:
        logging.error(f"Error en comando buscar: {e}")
        await temp_message.edit_text("Mis disculpas, señor. Ha fallado mi enlace con la red global o mi procesamiento de los datos.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    user_message = update.message.text
    save_message('user', user_message)
    
    history = get_context(limit=20)
    
    try:
        # Construir mensajes con el prompt del sistema + historial
        messages = [SYSTEM_PROMPT] + history
        
        # Ejecutamos la llamada a Ollama en un hilo separado para no bloquear el bot
        response = await asyncio.to_thread(
            ollama.chat,
            model=MODEL_NAME,
            messages=messages
        )
        
        bot_response = response['message']['content']
        
        save_message('assistant', bot_response)
        
        await update.message.reply_text(bot_response)
    except Exception as e:
        logging.error(f"Error en Ollama: {e}")
        await update.message.reply_text("Mis disculpas, señor. Parece que mi motor cognitivo principal ha sufrido un breve fallo. Sugiero revisar los registros del sistema.")

async def foto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update): return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text("Iniciando captura de pantalla de los sistemas principales, señor...")
    
    filepath = "screenshot.png"
    try:
        # Comando para macOS
        subprocess.run(["screencapture", "-x", filepath], check=True)
        
        # Enviar foto por Telegram
        with open(filepath, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption="Captura del sistema completada con éxito.")
            
        # Limpiar
        if os.path.exists(filepath):
            os.remove(filepath)
            
    except Exception as e:
        logging.error(f"Error al tomar o enviar captura de pantalla: {e}")
        await update.message.reply_text(f"Mis disculpas, señor. Ha ocurrido un error al intentar capturar la pantalla: {e}")

if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("foto", foto_command))
    app.add_handler(CommandHandler("buscar", buscar_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Servidor Jarvis arrancando con memoria conectada a SSD...")
    app.run_polling()
