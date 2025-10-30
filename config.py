import os

# ===============================
# CONFIGURACIÓN DE TOKENS Y CLAVES
# ===============================

# Token del bot de Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8190151176:AAG7U2m65c3rv5i8PE0XchN54Rb7uJLJeng")

# API Key de OpenAI (ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

# ===============================
# PARÁMETROS DEL BOT
# ===============================

# Tiempo en horas entre mensajes proactivos
MESSAGE_INTERVAL_HOURS = 2

# Nombre del archivo de la base de datos
DB_NAME = "database.db"

# Configuración del modelo de IA (ChatGPT)
OPENAI_MODEL = "gpt-3.5-turbo"

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
