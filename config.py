import os
from dotenv import load_dotenv

# ===============================
# CARGAR VARIABLES DESDE .env
# ===============================
load_dotenv()

# ===============================
# CONFIGURACIÓN DE TOKENS Y CLAVES
# ===============================

# Token del bot de Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# API Key de OpenAI (ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ===============================
# PARÁMETROS DEL BOT
# ===============================

# Tiempo en horas entre mensajes proactivos
MESSAGE_INTERVAL_HOURS = 2

# Nombre del archivo de la base de datos
DB_NAME = "database.db"

# Configuración del modelo de IA (ChatGPT)
OPENAI_MODEL = "gpt-4o-mini"

# ===============================
# MENSAJES PREDEFINIDOS
# ===============================

WELCOME_MESSAGE = (
    "👋 ¡Hola! Soy tu asistente emocional.\n\n"
    "Antes de empezar, elige con quién quieres hablar:\n\n"
    "💖 Lía — cercana, comprensiva y amable.\n"
    "😎 Sami — relajado, empático y positivo.\n\n"
    "Responde con 'Lía' o 'Sami' para comenzar."
)
