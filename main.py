import os
import sqlite3
import time
import threading
import schedule
import logging
from datetime import datetime
from typing import Optional

from config import TELEGRAM_TOKEN, OPENROUTER_API_KEY, DB_NAME, MESSAGE_INTERVAL_HOURS, AI_MODEL, WELCOME_MESSAGE

import telebot

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN no está definido en las variables de entorno")

bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")

ai_client = None
if OPENROUTER_API_KEY:
    try:
        from openai import OpenAI
        ai_client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        logging.info("OpenRouter cliente inicializado correctamente.")
    except Exception as e:
        logging.error("No se pudo inicializar OpenRouter: %s", e)
        ai_client = None
else:
    logging.warning("OPENROUTER_API_KEY no definido. El bot funcionará sin IA (fallback).")

DB_PATH = os.path.join(os.getcwd(), DB_NAME or "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    name TEXT,
                    personality TEXT,
                    schedule TEXT,
                    last_message TIMESTAMP,
                    mood TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    direction TEXT,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()
    logging.info("Base de datos inicializada en %s", DB_PATH)

def upsert_user(telegram_id:int, name:str, personality:str, schedule_period:str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (telegram_id, name, personality, schedule, last_message, mood)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
          name=excluded.name, personality=excluded.personality, schedule=excluded.schedule
    """, (telegram_id, name, personality, schedule_period, datetime.now(), "neutral"))
    conn.commit()
    conn.close()

def get_user_by_tg(tgid:int) -> Optional[tuple]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, telegram_id, name, personality, schedule, mood FROM users WHERE telegram_id=?", (tgid,))
    row = c.fetchone()
    conn.close()
    return row

def log_interaction(user_id:int, direction:str, message:str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO interactions (user_id, direction, message) VALUES (?, ?, ?)",
              (user_id, direction, message))
    conn.commit()
    conn.close()

RISK_KEYWORDS = ["suicid", "matarme", "me quiero morir", "no quiero vivir", "lastimarme", "quitarme la vida"]

def contains_risk(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in RISK_KEYWORDS)

def generate_ai_reply(system_prompt: str, user_message: str) -> str:
    if not ai_client:
        return "Lo siento — ahora mismo no puedo acceder al servicio de IA. ¿Quieres que intentemos algo simple juntos?"

    messages = [
        {"role":"system", "content": system_prompt},
        {"role":"user", "content": user_message}
    ]

    try:
        resp = ai_client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logging.exception("Error llamando a la IA: %s", e)
        return "Perdona, tuve un problema para generar mi respuesta. ¿Quieres intentarlo de nuevo?"

temp_state = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.from_user.id
    if uid in temp_state:
        del temp_state[uid]
    bot.send_message(message.chat.id, WELCOME_MESSAGE)

@bot.message_handler(func=lambda m: m.text and m.text in ["Lía", "Sami"])
def handle_personality(message):
    uid = message.from_user.id
    temp_state[uid] = {"personality": message.text}
    bot.send_message(message.chat.id, "Perfecto 😊 ¿Cómo te llamas?")

@bot.message_handler(func=lambda m: m.from_user and m.from_user.id in temp_state and "name" not in temp_state[m.from_user.id] and "personality" in temp_state[m.from_user.id])
def handle_name(message):
    uid = message.from_user.id
    if not message.text:
        return
    temp_state[uid]["name"] = message.text.strip()
    bot.send_message(message.chat.id, "¿En qué momento prefieres que te escriba? Responde: Mañana / Tarde / Noche")

@bot.message_handler(func=lambda m: m.from_user and m.from_user.id in temp_state and "schedule" not in temp_state[m.from_user.id] and "name" in temp_state[m.from_user.id])
def handle_schedule(message):
    uid = message.from_user.id
    if not message.text:
        return
    period = message.text.strip().lower()
    if period not in ["mañana", "tarde", "noche"]:
        bot.send_message(message.chat.id, "Por favor responde con: Mañana / Tarde / Noche")
        return
    data = temp_state.pop(uid)
    upsert_user(uid, data["name"], data["personality"], period)
    user = get_user_by_tg(uid)
    user_id = user[0] if user else None
    log_interaction(user_id, "in", f"Registro inicial: {data}")
    bot.send_message(message.chat.id, f"¡Perfecto, {data['name']}! Te escribiré por la {period}. Puedes escribirme cuando quieras 💬")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    uid = message.from_user.id
    
    if uid in temp_state:
        return
    
    user = get_user_by_tg(uid)
    if not user:
        bot.reply_to(message, "Primero ejecuta /start para configurar tu perfil.")
        return

    if not message.text:
        bot.reply_to(message, "Por favor envía un mensaje de texto.")
        return

    user_id = user[0]
    name = user[2]
    personality = user[3] or "Lía"
    mood = user[5] or "neutral"

    log_interaction(user_id, "in", message.text)

    if contains_risk(message.text):
        bot.send_message(message.chat.id,
                         "Siento mucho que te sientas así. Si estás en peligro inmediato, por favor contacta a emergencias locales. "
                         "Si quieres, puedo ofrecerte pasos para protegerte y recursos de ayuda.")
        log_interaction(user_id, "system", "detected_risk")
        return

    system_prompt = f"Eres {personality}, un asistente emocional empático. Contesta brevemente y con empatía. Si detectas riesgo recomienda ayuda profesional."
    user_prompt = f"Usuario ({name}, estado: {mood}): {message.text}"

    reply = generate_ai_reply(system_prompt, user_prompt)
    log_interaction(user_id, "out", reply)
    bot.send_message(message.chat.id, reply)

def current_period_utc():
    h = datetime.utcnow().hour
    if 5 <= h < 12:
        return "mañana"
    if 12 <= h < 18:
        return "tarde"
    return "noche"

def proactive_job():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    period = current_period_utc()
    c.execute("SELECT telegram_id, name, personality FROM users WHERE schedule=?", (period,))
    rows = c.fetchall()
    conn.close()
    for tg, name, personality in rows:
        text = f"Hola {name} 💛 ¿Cómo te sientes esta {period}?" if personality == "Lía" else f"¡Ey {name}! 😎 ¿Cómo va tu {period}?"
        try:
            bot.send_message(tg, text)
        except Exception as e:
            logging.warning("No se pudo enviar proactivo a %s: %s", tg, e)

schedule.every(MESSAGE_INTERVAL_HOURS).hours.do(proactive_job)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    init_db()
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()
    logging.info("Scheduler iniciado. Bot arrancando...")
    while True:
        try:
            bot.polling(non_stop=True, interval=1, timeout=60)
        except Exception as e:
            logging.exception("Error en polling, reintentando en 5s: %s", e)
            time.sleep(5)
