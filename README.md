# Jarvis-Claw (M4 Autonomous Agent)

Este repositorio contiene la configuración y el entorno de ejecución del agente autónomo de Aleix, basado en el framework oficial OpenClaw. Ejecutándose localmente en un Mac Mini M4 para automatización total de macOS, WhatsApp y Telegram.

## 🤖 ¿Qué es Jarvis-Claw?
Jarvis-Claw es un asistente y agente de automatización personal de inteligencia artificial de última generación. Está diseñado para simplificar tareas recurrentes operando directamente sobre el sistema (macOS) e interactuando con las plataformas de mensajería (WhatsApp y Telegram). 

Su propósito es servir como un verdadero asistente personal digital que tiene permisos y autonomía para ayudar en el flujo de trabajo y la automatización diaria, aprovechando la potencia local del procesador M4.

## ⚙️ Características principales
- **Control de Sistema:** Automatización de tareas de macOS de forma autónoma.
- **Interfaces de Comunicación:** Integrado con WhatsApp y Telegram para recibir órdenes de forma conversacional y remota.
- **Potencia Local:** Optimizando su ejecución en hardware de Apple Silicon (M4) para mayor velocidad y privacidad.

## 🛠️ Requisitos del sistema
- Mac Mini M4 (recomendado) o equipo compatible con macOS.
- Permisos de Accesibilidad y Control de Pantalla en macOS para la automatización.
- Node.js y Python (versiones compatibles).
- Claves de API (ver sección de configuración).

## 🚀 Instalación y Uso
1. **Clonar el repositorio:**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd aleix_jarvis
   ```
2. **Configurar el entorno:**
   - Copia el archivo `.env.example` a `.env` y añade las credenciales necesarias (APIs de mensajería, LLMs, etc.).
   - Asegúrate de que el `.env` está copiado también en el directorio de `openclaw/`.
3. **Instalación de dependencias y ejecución:**
   *(Consultar la documentación específica de [OpenClaw](GUIA_OPENCLAW.md) para más detalles sobre cómo arrancar los servicios).*

## ⚠️ Advertencia de Seguridad
Este agente está diseñado para tener control sobre el sistema operativo. Úsese con precaución y asegúrese de no exponer las claves de las APIs ni los puertos de control a redes no confiables.
