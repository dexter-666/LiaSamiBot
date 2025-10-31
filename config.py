import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MESSAGE_INTERVAL_HOURS = 2
DB_NAME = "database.db"
AI_MODEL = "google/gemini-2.0-flash-exp:free"

WELCOME_MESSAGE = (
    "👋 ¡Hola! Soy tu asistente emocional.\n\n"
    "Antes de empezar, elige con quién quieres hablar:\n\n"
    "💖 Lía — cercana, comprensiva y amable.\n"
    "😎 Sami — relajado, empático y positivo.\n\n"
    "Responde con 'Lía' o 'Sami' para comenzar."
)
