# Jarvis - Asistente Personal de Telegram (Local AI)

Este proyecto es un bot de Telegram diseñado para actuar como **Jarvis**, el asistente de IA personal de Aleix. Se ejecuta de forma local en un Mac Mini M4 y utiliza [Ollama](https://ollama.ai/) para procesar lenguaje natural utilizando el modelo `llama3`.

El bot tiene una personalidad predefinida: responde siempre en español, con un tono profesional, eficiente y con un toque de ingenio británico, imitando al Jarvis de Iron Man.

## ✨ Características

*   **Inteligencia Artificial Local**: Utiliza Ollama con el modelo `llama3` ejecutándose completamente en local, lo que garantiza la privacidad de los datos.
*   **Seguridad Estricta**: El bot está restringido para responder **únicamente** a un usuario específico (definido por su ID de Telegram). Ignorará cualquier mensaje de otros usuarios.
*   **Memoria Persistente (SSD)**: Jarvis mantiene un historial de los mensajes utilizando una base de datos SQLite configurada para almacenarse en un disco SSD externo. Esto proporciona contexto a largo plazo y sobrevive a reinicios del bot.
*   **Capturas del Sistema**: Incluye un comando `/foto` para tomar capturas de pantalla del Mac Mini de forma remota y enviarlas por Telegram.
*   **Mantenimiento Automático**: Un script nocturno configurado vía `cron` se encarga de mantener actualizado el modelo de IA y envía reportes de mantenimiento por Telegram.
*   **Procesamiento Asíncrono**: Las llamadas al modelo de IA se realizan en hilos separados para no bloquear la recepción de nuevos mensajes en Telegram.
*   **Personalidad a Medida**: Prompt de sistema integrado para comportarse como el icónico asistente virtual.

## 📋 Requisitos Previos

Para ejecutar este bot, necesitarás:

1.  **Python 3.8+** instalado.
2.  **Ollama** instalado y ejecutándose en tu máquina.
3.  El modelo `llama3` descargado en Ollama. Puedes descargarlo ejecutando en tu terminal:
    ```bash
    ollama run llama3
    ```
4.  Un **Token de Bot de Telegram** (obtenido a través de [@BotFather](https://t.me/botfather)).
5.  Tu **ID de Usuario de Telegram** (puedes obtenerlo hablando con bots como [@userinfobot](https://t.me/userinfobot)).
6.  Un **SSD o unidad de almacenamiento externo** donde alojar la memoria (opcional pero recomendado).

## 🚀 Instalación y Configuración

1.  **Clona o descarga** este repositorio.

2.  **Instala las dependencias** necesarias usando pip:
    ```bash
    pip install python-telegram-bot python-dotenv ollama
    ```

3.  **Configura las variables de entorno**:
    Crea un archivo llamado `.env` en la raíz del proyecto y añade tus credenciales y rutas:
    ```env
    TELEGRAM_TOKEN="tu_token_de_telegram_aqui"
    USER_ID=tu_id_de_usuario_aqui
    DB_PATH="/Volumes/USB/jarvis_memory.db"
    ```

4.  **Configura el Mantenimiento Nocturno**:
    Haz ejecutable el script de actualización:
    ```bash
    chmod +x update_jarvis.sh
    ```
    Luego, añádelo a tu crontab para que se ejecute diariamente (por ejemplo, a las 04:00 AM):
    ```bash
    crontab -e
    # Añadir: 0 4 * * * /ruta/absoluta/a/tu/proyecto/update_jarvis.sh
    ```

## ⚙️ Uso

Para iniciar el servidor de Jarvis, simplemente ejecuta el script principal o lánzalo en segundo plano con `nohup`:

```bash
nohup python3 bot.py > bot_output.log 2>&1 &
```

A partir de este momento, puedes ir a Telegram, buscar tu bot y enviarle el comando `/start`. Jarvis se presentará, inicializará su memoria SSD y estará listo para asistirte.

### Comandos de Telegram

* `/start` - Inicializa a Jarvis y comprueba el estado del sistema.
* `/foto` - Toma una captura de pantalla del Mac Mini M4 y te la envía al chat.
* `(Cualquier texto)` - Habla naturalmente con Jarvis. Él recordará el contexto gracias a su memoria persistente en SQLite.

## 📝 Estructura del Código

*   `bot.py`: Contiene toda la lógica principal del bot, la conexión con Telegram, la base de datos SQLite y la integración con la API local de Ollama.
*   `update_jarvis.sh`: Script en Bash independiente para mantener actualizado el modelo `llama3` y notificar al usuario.
*   `.env`: Archivo (no incluido en el repositorio por seguridad) que almacena de forma segura el token, ID de usuario y la ruta del SSD.
*   `bot.log` / `bot_output.log`: Archivos generados automáticamente donde se registran eventos y posibles errores del sistema.

## 🔒 Privacidad y Seguridad

Al ejecutar el modelo de lenguaje de forma local mediante Ollama, ninguna parte de tus conversaciones se envía a servidores de terceros (como OpenAI o Google). Toda la inferencia ocurre en tu propia máquina (Mac Mini M4). Tu historial de conversación permanece completamente privado dentro de tu archivo SQLite en tu SSD. Además, el filtro por `USER_ID` evita que otras personas interactúen con tu instancia de Jarvis o usen los comandos de sistema.