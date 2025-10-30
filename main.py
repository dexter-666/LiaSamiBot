import telebot
import sqlite3
import time, threading, schedule
from datetime import datetime
from openai import OpenAI

# --- CLAVES DIRECTAMENTE ---
OPENAI_API_KEY = "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"
TELEGRAM_TOKEN = "8190151176:AAG7U2m65c3rv5i8PE0XchN54Rb7uJLJeng"

# Inicializar clientes
bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai = OpenAI(api_key=OPENAI_API_KEY)

# --- Inicializar base de datos ---
def init_db():
    conn = sqlite3.connect('emobot.db')
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
    conn.commit()
    conn.close()

init_db()

# --- Variables temporales ---
temp_data = {}

# --- /start ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message,
        "👋 ¡Hola! Soy tu asistente emocional IA.\n"
        "Antes de comenzar, elige con quién quieres hablar:\n\n"
        "💖 Lía — cercana, empática y calmada.\n"
        "😎 Sami — relajado, motivador y alegre.\n\n"
        "Responde con 'Lía' o 'Sami' para continuar."
    )

# --- Selección de personalidad ---
@bot.message_handler(func=lambda m: m.text in ['Lía', 'Sami'])
def ask_name(message):
    temp_data[message.from_user.id] = {'personality': message.text}
    bot.send_message(message.chat.id, "Genial 😊 ¿Cómo te llamas?")

# --- Guardar nombre ---
@bot.message_handler(func=lambda m: m.from_user.id in temp_data and 'name' not in temp_data[m.from_user.id])
def ask_schedule(message):
    temp_data[m.from_user.id]['name'] = message.text
    bot.send_message(message.chat.id,
        f"Encantado/a, {message.text} 💫\n"
        "¿En qué momento prefieres conversar conmigo?\n"
        "🌅 Mañana / 🌇 Tarde / 🌙 Noche"
    )

# --- Guardar usuario completo ---
@bot.message_handler(func=lambda m: m.from_user.id in temp_data and 'schedule' not in temp_data[m.from_user.id])
def save_user(message):
    horario = message.text.lower()
    if horario not in ['mañana', 'tarde', 'noche']:
        bot.send_message(message.chat.id, "Por favor responde con: Mañana, Tarde o Noche ☀️")
        return

    data = temp_data[m.from_user.id]
    conn = sqlite3.connect('emobot.db')
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO users (telegram_id, name, personality, schedule, last_message, mood)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (message.from_user.id, data['name'], data['personality'], horario, datetime.now(), 'neutral'))
    conn.commit()
    conn.close()
    del temp_data[m.from_user.id]

    bot.send_message(message.chat.id, f"Perfecto, {data['name']} 😄. Te escribiré principalmente por la {horario}. Puedes hablar conmigo cuando quieras 💬.")

# --- Chat libre con IA ---
@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    user_id = message.from_user.id
    conn = sqlite3.connect('emobot.db')
    c = conn.cursor()
    c.execute("SELECT name, personality, mood FROM users WHERE telegram_id=?", (user_id,))
    user = c.fetchone()
    conn.close()

    if not user:
        bot.reply_to(message, "Primero inicia con /start para configurar tu perfil ✨")
        return

    name, personality, mood = user
    prompt = f"""
Eres {personality}, un asistente emocional empático que brinda apoyo personal.
El usuario se llama {name}. Su estado de ánimo actual es {mood}.
Responde de forma natural, cálida y con frases breves, como un amigo que escucha.
Mensaje del usuario: {message.text}
    """

    try:
        response = ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        bot.send_message(message.chat.id, answer)

        # Guardar último mensaje y actualizar estado emocional
        conn = sqlite3.connect('emobot.db')
        c = conn.cursor()
        c.execute("UPDATE users SET last_message=? WHERE telegram_id=?", (datetime.now(), user_id))
        conn.commit()
        conn.close()

    except Exception as e:
        bot.send_message(message.chat.id, "😔 Estoy teniendo problemas para responder. Intenta de nuevo más tarde.")

# --- Envío proactivo cada 3 horas ---
def proactive_messages():
    conn = sqlite3.connect('emobot.db')
    c = conn.cursor()
    now_hour = datetime.now().hour
    if 5 <= now_hour < 12:
        period = "mañana"
    elif 12 <= now_hour < 18:
        period = "tarde"
    else:
        period = "noche"

    c.execute("SELECT telegram_id, name, personality FROM users WHERE schedule=?", (period,))
    users = c.fetchall()
    conn.close()

    for uid, name, personality in users:
        text = f"Hola {name} 💛 ¿Cómo te sientes esta {period}?" if personality == "Lía" else f"¡Ey {name}! 😎 ¿Todo bien esta {period}?"
        bot.send_message(uid, text)

schedule.every(3).hours.do(proactive_messages)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_scheduler, daemon=True).start()

bot.polling(none_stop=True)
