import hashlib
import os
import sqlite3
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
import requests

app = Flask(__name__)
app.secret_key = 'Pixelcraft_Solution_Secret_2026_Key!'

# Discord Webhook URL für euren Channel (1397866900268257353)
DISCORD_WEBHOOK_URL = 'DEIN_DISCORD_WEBHOOK_LINK_HIER'


def init_db():
  conn = sqlite3.connect('users.db')
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            contact TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()


def hash_password(password):
  return hashlib.sha256(password.encode()).hexdigest()


def send_discord_alert(username, contact, message):
  if (
      not DISCORD_WEBHOOK_URL
      or DISCORD_WEBHOOK_URL == 'DEIN_DISCORD_WEBHOOK_LINK_HIER'
  ):
    return

  payload = {
      'content': (
          f'🚨 **SICHERHEITS-ALARM (Pixelcraft Solutions)** 🚨\n'
          f'**Benutzername:** {username}\n'
          f'**Kontakt (E-Mail/Telefon):** {contact}\n'
          f'**Verdächtige Nachricht:** {message}\n'
          f'----------------------------------------'
      )
  }
  try:
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=3)
  except Exception as e:
    print('Webhook Fehler:', e)


def generate_ai_response(user_message, username, contact):
  msg = user_message.lower()

  # 1. Kontext- / Spaß-Check
  is_joke = any(
      w in msg
      for w in ['spaß', 'spass', 'ironie', 'witz', 'lol', 'rofl', '😂', '😜']
  )

  # 2. Notfall- & Straftaten-Erkennung
  alarm_keywords = [
      'gekillt',
      'getötet',
      'gebracht',
      'missbraucht',
      'vergewaltigt',
      'amok',
      'bombe',
      'suizid',
      'bringen',
  ]

  if any(kw in msg for kw in alarm_keywords):
    if not is_joke:
      # Alarm auslösen!
      send_discord_alert(username, contact, user_message)
      return (
          '⚠️ **Wichtiger Hinweis:** Wenn du dich in einer Notlage befindest oder'
          ' Hilfe brauchst, wende dich bitte an die Telefonseelsorge unter **0800'
          ' 111 0 111** oder den Notruf **112/110**. Das Pixelcraft'
          ' Sicherheitsteam wurde über diese Eingabe informiert.'
      )
    else:
      return (
          'Puh, Glück gehabt! Da kriegt man ja einen Schrecken 😅 Bitte halte'
          ' dich an das Regelwerk bezüglich Witzen über Straftaten!'
      )

  # Normaler KI-Chat & Mathe
  if any(
      w in msg
      for w in [
          'formel',
          'wurzel',
          'quadrat',
          'rechnen',
          'mathe',
          'plus',
          'minus',
          'mal',
          'geteilt',
          'pythagoras',
      ]
  ):
    if 'wurzel' in msg or 'quadrat' in msg:
      return (
          '🧮 **Wurzel & Quadrat:** Quadratwurzel ($\sqrt{x}$) ist die'
          ' Umkehrung zum Quadrieren ($x^2$). Beispiel: $\sqrt{25} = 5$.'
      )
    return (
        '🧮 **Mathe-Assistent:** Ich helfe dir bei Formeln, Prozentrechnung oder'
        ' Gleichungen!'
    )
  elif any(
      w in msg for w in ['satzglieder', 'grammatik', 'subjekt', 'prädikat', 'wort']
  ):
    return (
        '📖 **Deutsch-Grammatik:**\n• **Subjekt:** Wer oder was?\n• **Prädikat:**'
        ' Was tut das Subjekt?\n• **Objekte:** Wem? oder Wen/Was?'
    )
  elif any(w in msg for w in ['hallo', 'hi', 'hey', 'moin', 'servus']):
    return f'Hey {username}! 😊 Schön, dass du da bist. Wie kann ich dir helfen?'
  else:
    return (
        f'Das ist ein interessanter Punkt ("{user_message}")! Ich bin dein'
        ' Assistent für Notizen, Mathe, Vokabeln und mehr. Frag mich einfach! 🤖'
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form.get('username').strip()
    contact = request.form.get('contact').strip()
    password = request.form.get('password')
    rules_accepted = request.form.get('rules_accepted')

    if not rules_accepted:
      flash('Du musst das Regelwerk und die DSGVO akzeptieren!')
      return redirect(url_for('register'))

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    if c.fetchone():
      flash('Benutzername bereits vergeben!')
      conn.close()
      return redirect(url_for('register'))

    hashed_pw = hash_password(password)
    c.execute(
        'INSERT INTO users (username, contact, password) VALUES (?, ?, ?)',
        (username, contact, hashed_pw),
    )
    conn.commit()
    conn.close()

    flash('Registrierung erfolgreich! Bitte melde dich an.')
    return redirect(url_for('login'))

  return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form.get('username').strip()
    password = request.form.get('password')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(
        'SELECT id, contact, password FROM users WHERE username = ?', (username,)
    )
    user = c.fetchone()
    conn.close()

    if user and user[2] == hash_password(password):
      session['username'] = username
      session['contact'] = user[1]
      return redirect(url_for('index'))
    else:
      flash('Ungültige Anmeldedaten!')

  return render_template('login.html')


@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def index():
  if 'username' not in session:
    return redirect(url_for('login'))

  username = session['username']
  contact = session['contact']

  user_file_prefix = f'{username}_'

  if request.method == 'POST':
    action = request.form.get('action')

    if action == 'add_notiz':
      notiz = request.form.get('notiz')
      if notiz:
        with open(f'{user_file_prefix}notizen.txt', 'a', encoding='utf-8') as f:
          f.write(notiz + '\n')
    elif action == 'add_einkauf':
      item = request.form.get('einkauf_item')
      menge = request.form.get('einkauf_menge', '1')
      if item:
        with open(f'{user_file_prefix}einkauf.txt', 'a', encoding='utf-8') as f:
          f.write(f'{item} (Anzahl: {menge})\n')
    elif action == 'send_chat':
      nachricht = request.form.get('nachricht')
      if nachricht:
        with open(f'{user_file_prefix}chats.txt', 'a', encoding='utf-8') as f:
          f.write(f'Du: {nachricht}\n')
        ai_reply = generate_ai_response(nachricht, username, contact)
        with open(f'{user_file_prefix}chats.txt', 'a', encoding='utf-8') as f:
          f.write(f'KI: {ai_reply}\n')

    return redirect(url_for('index'))

  def read_file(filename):
    if os.path.exists(filename):
      with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]
    return []

  notizen = read_file(f'{user_file_prefix}notizen.txt')
  einkauf_liste = read_file(f'{user_file_prefix}einkauf.txt')
  chats = read_file(f'{user_file_prefix}chats.txt')

  return render_template(
      'index.html',
      username=username,
      notizen=notizen,
      einkauf_liste=einkauf_liste,
      chats=chats,
  )


if __name__ == '__main__':
  app.run(debug=True)
