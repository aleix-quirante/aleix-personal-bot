# Jarvis-Claw: Autonomous macOS Agent

Agente autónomo de control de sistema operativo desplegado sobre un entorno Apple Mac Mini (M4). Utiliza el framework OpenClaw para la ejecución directa de comandos shell y control de interfaz de usuario (UI) de manera desatendida.

## Arquitectura

El sistema opera de forma estrictamente local (Sabadell Node), empleando Modelos de Lenguaje Grandes (LLMs) para el razonamiento de tareas y la toma de decisiones. La ejecución física de las acciones resultantes se delega directamente a la capa de sistema operativo de macOS. La interfaz de ingesta de comandos y monitorización se realiza a través de la API de Telegram, proporcionando un canal de comunicación seguro y bidireccional.

## Configuración Crítica

Para el correcto funcionamiento autónomo del agente, es imperativo aplicar las siguientes configuraciones en el entorno:

1. **Auto-Run Habilitado**: Se requiere la modificación del parámetro `require_approval` a `false`. Esto elimina la necesidad de confirmación manual para la ejecución de comandos.
2. **System Prompt**: Es obligatoria la inyección de un System Prompt específicamente contextualizado a las capacidades y restricciones del hardware subyacente (Apple Mac Mini M4).

## Despliegue

Para inicializar el agente, posicione el contexto de ejecución en el subdirectorio del framework y proceda con la instalación de dependencias y el arranque del servicio:

```bash
cd openclaw/
npm install
npm run start
```
