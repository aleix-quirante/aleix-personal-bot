# Jarvis - Asistente Personal de Telegram (Local AI)

Este proyecto es un bot de Telegram diseñado para actuar como **Jarvis**, el asistente de IA personal de Aleix. Se ejecuta de forma local en un Mac Mini M4 y utiliza [Ollama](https://ollama.ai/) para procesar lenguaje natural utilizando el modelo `llama3`.

El bot tiene una personalidad predefinida: responde siempre en español, con un tono profesional, eficiente y con un toque de ingenio británico, imitando al Jarvis de Iron Man.

## ✨ Características

*   **Inteligencia Artificial Local**: Utiliza Ollama con el modelo `llama3` ejecutándose completamente en local, lo que garantiza la privacidad de los datos.
*   **Seguridad Estricta**: El bot está restringido para responder **únicamente** a un usuario específico (definido por su ID de Telegram). Ignorará cualquier mensaje de otros usuarios.
*   **Memoria de Conversación**: Jarvis mantiene un historial de los últimos mensajes (configurable) para tener contexto en la conversación y ofrecer respuestas más coherentes.
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

## 🚀 Instalación y Configuración

1.  **Clona o descarga** este repositorio.

2.  **Instala las dependencias** necesarias usando pip:
    ```bash
    pip install python-telegram-bot python-dotenv ollama
    ```

3.  **Configura las variables de entorno**:
    Crea un archivo llamado `.env` en la raíz del proyecto y añade tus credenciales:
    ```env
    TELEGRAM_TOKEN=tu_token_de_telegram_aqui
    USER_ID=tu_id_de_usuario_aqui
    ```

## ⚙️ Uso

Para iniciar el servidor de Jarvis, simplemente ejecuta el script principal:

```bash
python bot.py
```

Verás un mensaje en la consola indicando: `🚀 Servidor Jarvis arrancando con su nueva personalidad...`

A partir de este momento, puedes ir a Telegram, buscar tu bot y enviarle el comando `/start`. Jarvis se presentará y estará listo para asistirte.

## 📝 Estructura del Código

*   `bot.py`: Contiene toda la lógica principal del bot, la conexión con Telegram y la integración con la API local de Ollama.
*   `.env`: Archivo (no incluido en el repositorio por seguridad) que almacena de forma segura el token y el ID de usuario.
*   `bot.log`: Archivo generado automáticamente donde se registran eventos y posibles errores del sistema.

## 🔒 Privacidad y Seguridad

Al ejecutar el modelo de lenguaje de forma local mediante Ollama, ninguna parte de tus conversaciones se envía a servidores de terceros (como OpenAI o Google). Toda la inferencia ocurre en tu propia máquina (Mac Mini M4). Además, el filtro por `USER_ID` evita que otras personas interactúen con tu instancia de Jarvis.