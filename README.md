# Bot de Telegram con IA Emocional

Bot de Telegram que funciona como asistente emocional usando IA (OpenRouter). Permite a los usuarios elegir entre dos personalidades (Lía y Sami) y mantiene conversaciones empáticas.

## 🚀 Características

- **Dos personalidades**: Lía (cercana y comprensiva) y Sami (relajado y empático)
- **IA conversacional**: Usa OpenRouter para acceder a múltiples modelos de IA
- **Mensajes proactivos**: El bot puede escribir a los usuarios en horarios configurados
- **Base de datos**: Guarda historial de conversaciones y preferencias de usuarios
- **Detección de riesgo**: Identifica palabras clave de riesgo emocional

## 📋 Requisitos

- Python 3.11+
- Token de Bot de Telegram (obtenerlo de [@BotFather](https://t.me/BotFather))
- API Key de OpenRouter (obtenerla en [openrouter.ai](https://openrouter.ai))

## ⚙️ Instalación

1. **Clona el repositorio**:
```bash
git clone <tu-repositorio>
cd <nombre-del-proyecto>
```

2. **Instala las dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configura las variables de entorno**:

Crea un archivo `.env` basado en `.env.example`:
```bash
cp .env.example .env
```

Edita el archivo `.env` y agrega tus credenciales:
```
TELEGRAM_TOKEN=tu_token_de_telegram
OPENROUTER_API_KEY=tu_api_key_de_openrouter
```

4. **Ejecuta el bot**:
```bash
python main.py
```

## 📁 Estructura del Proyecto

```
.
├── main.py              # Código principal del bot
├── config.py            # Configuración y variables
├── requirements.txt     # Dependencias de Python
├── .env.example        # Plantilla de variables de entorno
├── .gitignore          # Archivos ignorados por Git
└── README.md           # Este archivo
```

## 🤖 Uso del Bot

1. Inicia una conversación con tu bot en Telegram
2. Envía `/start`
3. Elige personalidad: "Lía" o "Sami"
4. Escribe tu nombre
5. Selecciona horario preferido: "Mañana", "Tarde" o "Noche"
6. ¡Comienza a chatear!

## 🔧 Configuración

Puedes modificar estos parámetros en `config.py`:

- `MESSAGE_INTERVAL_HOURS`: Intervalo de mensajes proactivos (default: 2 horas)
- `AI_MODEL`: Modelo de IA a usar (default: "meta-llama/llama-3.1-8b-instruct:free")
- `WELCOME_MESSAGE`: Mensaje de bienvenida personalizado

### Modelos disponibles en OpenRouter

Puedes cambiar el modelo en `config.py`. Algunos modelos gratuitos:
- `meta-llama/llama-3.1-8b-instruct:free` (gratuito)
- `google/gemini-2.0-flash-exp:free` (gratuito)
- `mistralai/mistral-7b-instruct:free` (gratuito)

Modelos de pago (más potentes):
- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4-turbo`
- `google/gemini-pro-1.5`

Ver todos los modelos en: https://openrouter.ai/models

## 🗄️ Base de Datos

El bot usa SQLite (`database.db`) para almacenar:
- Información de usuarios (nombre, personalidad, horario preferido)
- Historial de interacciones
- Estado emocional

**Nota**: `database.db` está en `.gitignore` y no se sube a GitHub.

## 🚫 Lo que YA NO necesitas

- ❌ **OPENAI_API_KEY**: Ya no usamos OpenAI directamente
- ❌ **python-dotenv**: No es necesario, usamos variables de entorno directamente
- ❌ **aiogram**: Eliminado, solo usamos pyTelegramBotAPI

## 📝 Archivos necesarios para GitHub

Solo necesitas subir estos archivos:
- ✅ `main.py`
- ✅ `config.py`
- ✅ `requirements.txt`
- ✅ `.env.example`
- ✅ `.gitignore`
- ✅ `README.md`

**NO subas**:
- ❌ `.env` (contiene tus claves secretas)
- ❌ `database.db` (base de datos local)
- ❌ `__pycache__/` (archivos temporales de Python)

## 📦 Dependencias

El bot usa las siguientes librerías principales:
- `pyTelegramBotAPI`: Para interactuar con Telegram
- `openai`: SDK compatible con OpenRouter
- `httpx`: Cliente HTTP (versión específica para compatibilidad)
- `schedule`: Para mensajes programados

## 🛡️ Seguridad

- Nunca compartas tu archivo `.env`
- Nunca subas credenciales a GitHub
- Las claves de API están en variables de entorno

## 📄 Licencia

Proyecto de uso personal.

## 👤 Autor

Tu nombre aquí
