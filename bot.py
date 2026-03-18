import os
import re
import logging
import asyncio
import json
import sqlite3
import subprocess
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from duckduckgo_search import DDGS

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Inicializamos el modelo de Gemini con las instrucciones de sistema
jarvis_model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction="Eres Jarvis, el asistente personal de Aleix. Eres directo, eficiente, educado y muy obediente. Tu trabajo es ayudar a Aleix y responder a sus preguntas con tu conocimiento general actualizado. Responde siempre de forma concisa.",
)

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_ID = int(os.getenv("USER_ID", "0"))
DB_PATH = "/Volumes/USB/jarvis_memory.db"  # Ruta directa al SSD

logging.basicConfig(level=logging.INFO, filename="bot.log")


# --- MEMORIA ---
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.close()


def save_message(role, content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()


def get_context(limit=15):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM (SELECT * FROM messages ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"role": r, "content": c} for r, c in rows]
    except:
        return []


# --- AUTOMATIZACIÓN WHATSAPP (EL CORAZÓN) ---
def buscar_contacto_mac(nombre_buscar):
    # Dividimos el nombre en palabras sueltas
    palabras = nombre_buscar.strip().split()
    if not palabras:
        return None

    # Construimos una condición flexible en AppleScript
    # Ej: name contains "antonio" and name contains "quirante"
    condiciones = " and ".join([f'name contains "{p}"' for p in palabras])

    applescript = f"""
    tell application "Contacts"
        try
            -- Búsqueda elástica: Ignora si hay segundos nombres o apellidos entre medias
            set laPersona to first person whose {condiciones}
            set elNumero to value of first phone of laPersona
            return elNumero
        on error
            return "NO_ENCONTRADO"
        end try
    end tell
    """
    try:
        resultado = subprocess.run(
            ["osascript", "-e", applescript], capture_output=True, text=True
        )
        numero_bruto = resultado.stdout.strip()

        if numero_bruto == "NO_ENCONTRADO" or not numero_bruto:
            return None

        return re.sub(r"\D", "", numero_bruto)
    except Exception as e:
        logging.error(f"Error buscando contacto: {e}")
        return None


async def enviar_whatsapp(contacto, mensaje, update):
    c_limpio = (
        contacto.lower()
        .replace("jarvis", "")
        .replace("al ", "")
        .replace("a ", "")
        .strip()
    )
    await update.message.reply_text(
        f"Jarvis: Buscando a {c_limpio.title()} en sus contactos..."
    )

    numero = buscar_contacto_mac(c_limpio)

    if not numero:
        await update.message.reply_text(
            f"❌ Jarvis: Disculpe, señor. No encuentro a nadie llamado '{c_limpio.title()}' en su agenda."
        )
        return False

    logging.info(f"Enviando WhatsApp a {c_limpio} ({numero})")
    mensaje_codificado = urllib.parse.quote(mensaje)
    url_whatsapp = f"whatsapp://send?phone={numero}&text={mensaje_codificado}"

    try:
        # Abrir WhatsApp directo en el chat
        subprocess.run(["open", url_whatsapp], check=True)

        # Pausa para asegurar que la app carga y el cursor está listo
        await asyncio.sleep(3.5)

        # APPLESCRIPT SIMPLIFICADO AL MÁXIMO
        subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "WhatsApp" to activate',
                "-e",
                "delay 0.8",
                "-e",
                'tell application "System Events" to key code 36',
            ],
            check=True,
        )

        await update.message.reply_text(
            f"✅ Protocolo completado. Mensaje entregado a {c_limpio.title()}."
        )
        return True

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error crítico en los servos de WhatsApp: {e}"
        )
        return False


# --- PROCESAMIENTO ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        logging.warning(
            f"Intento de acceso no autorizado del ID: {update.effective_user.id}"
        )
        return

    user_text = update.message.text
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    save_message("user", user_text)
    history = get_context(limit=6)
    historial_texto = "\n".join(
        [
            f"{'Usuario' if m['role']=='user' else 'Jarvis'}: {m['content']}"
            for m in history
        ]
    )

    # 1. ¿Quiere enviar un mensaje?
    intent_prompt = f"Historial:\n{historial_texto}\n\nOrden: '{user_text}'\n¿La orden te pide enviar un mensaje a alguien por WhatsApp/Telegram? Responde SOLO SI o NO."
    intent_res = await asyncio.to_thread(jarvis_model.generate_content, intent_prompt)

    if "SI" in intent_res.text.upper():
        extract_prompt = f"""Historial reciente:
{historial_texto}

Última orden a procesar: '{user_text}'

REGLAS:
1. Extrae el nombre del destinatario exactamente como lo ha escrito el usuario.
2. Si no hay nombre en la orden actual, dedúcelo del historial.
3. Extrae el mensaje.
4. Devuelve el resultado en JSON.
"""
        try:
            # Gemini 1.5 soporta forzar salida JSON nativa
            extract_res = await asyncio.to_thread(
                jarvis_model.generate_content,
                extract_prompt,
                generation_config={"response_mime_type": "application/json"},
            )

            data = json.loads(extract_res.text)
            await enviar_whatsapp(data["c"], data["m"], update)
            save_message(
                "assistant",
                f"Acción completada: Mensaje enviado a {data['c']}. Contenido: {data['m']}",
            )
            return

        except Exception as e:
            logging.error(f"Error procesando JSON con Gemini: {e}")
            await update.message.reply_text(
                "❌ Jarvis: Mis sistemas no pudieron aislar el destinatario o el mensaje. ¿Podría repetirlo?"
            )
            save_message("assistant", "Fallo al procesar el envío.")
            return

    # 2. Captura de pantalla
    if any(k in user_text.lower() for k in ["foto", "pantalla", "captura"]):
        subprocess.run(["screencapture", "-x", "snap.png"])
        await update.message.reply_photo(
            photo=open("snap.png", "rb"), caption="Sistemas visuales activos."
        )
        save_message("assistant", "He enviado una captura de pantalla al usuario.")
        return

    # 3. Charla normal e Internet (Gemini lo hace todo)
    chat_prompt = f"Historial reciente:\n{historial_texto}\n\nEl usuario dice: '{user_text}'\nResponde como Jarvis directamente al usuario."

    try:
        chat_res = await asyncio.to_thread(jarvis_model.generate_content, chat_prompt)
        reply = chat_res.text
        save_message("assistant", reply)
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Error en el chat de Gemini: {e}")
        await update.message.reply_text(
            "❌ Jarvis: Error de conexión con mis servidores centrales."
        )


if __name__ == "__main__":
    init_db()
    print("🚀 Jarvis en línea. Mac Mini M4 bajo control.")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
