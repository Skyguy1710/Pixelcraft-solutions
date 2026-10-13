import hashlib
import os
import sqlite3
from datetime import timedelta
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
app.permanent_session_lifetime = timedelta(days=30)

DISCORD_WEBHOOK_URL = 'DEIN_DISCORD_WEBHOOK_LINK_HIER'


def get_db_connection():
  conn = sqlite3.connect('users.db')
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  conn = get_db_connection()
  c = conn.cursor()
  # User-Tabelle erstellen falls nicht vorhanden
  c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            contact TEXT NOT NULL,
            password TEXT NOT NULL,
            roles TEXT DEFAULT '',
            hide_contact INTEGER DEFAULT 0
        )
    """)

  # Falls die Tabelle schon älter war und Spalten fehlen, fügen wir sie sicherheitshalber hinzu
  try:
    c.execute('ALTER TABLE users ADD COLUMN roles TEXT DEFAULT ""')
  except Exception:
    pass
  try:
    c.execute('ALTER TABLE users ADD COLUMN hide_contact INTEGER DEFAULT 0')
  except Exception:
    pass

  # Admin-Tabelle
  c.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT UNIQUE NOT NULL
        )
    """)
  conn.commit()

  for adm in ['SkyGuy', 'Ghost_rider272']:
    c.execute('INSERT OR IGNORE INTO admins (username) VALUES (?)', (adm,))
  conn.commit()
  conn.close()


try:
  init_db()
except Exception as e:
  print('DB Init Exception:', e)


def hash_password(password):
  return hashlib.sha256(password.encode()).hexdigest()


def get_user_roles(username):
  if not username:
    return []
  conn = get_db_connection()
  c = conn.cursor()
  c.execute('SELECT roles FROM users WHERE username = ?', (username,))
  row = c.fetchone()
  conn.close()
  if row and row['roles']:
    return [r.strip() for r in row['roles'].split(',') if r.strip()]
  return []


def is_admin_user(username):
  if not username:
    return False
  if username.lower() == 'skyguy':
    return True

  conn = get_db_connection()
  c = conn.cursor()
  c.execute('SELECT 1 FROM admins WHERE username = ?', (username,))
  res = c.fetchone()
  conn.close()
  if res:
    return True

  roles = get_user_roles(username)
  admin_roles = [
      'CEO',
      'CTO',
      'COO',
      'Director of Development & Technical',
      'Project Lead',
      'Deputy Project Lead',
      'Operations / Community Director',
      'Business Development Manager',
      'Project Manager',
      'Product Manager',
      'Lead Developer',
      'Developer',
      'Bot Developer',
      'Script Developer',
      'UI/UX Designer',
      'QA-Tester (Quality Assurance)',
      'Cybersecurity Analyst',
  ]
  for r in roles:
    if r in admin_roles:
      return True

  return False


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
  is_joke = any(
      w in msg
      for w in ['spaß', 'spass', 'ironie', 'witz', 'lol', 'rofl', '😂', '😜']
  )
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
      send_discord_alert(username, contact, user_message)
      return (
          '⚠️ **Wichtiger Hinweis:** Wenn du dich in einer Notlage befindest oder'
          ' Hilfe brauchst, wende dich bitte an die Telefonseelsorge unter **0800'
          ' 111 0 111** oder den Notruf **112/110**. Das Pixelcraft'
          ' Sicherheitsteam wurde informiert.'
      )
    else:
      return (
          'Puh, Glück gehabt! Da kriegt man ja einen Schrecken 😅 Bitte halte'
          ' dich an das Regelwerk bezüglich Witzen über Straftaten!'
      )

  if 'adverbial' in msg or 'bestimmung' in msg or 'zeit' in msg:
    return (
        '📖 **Adverbiale Bestimmung (Adverbialangabe):**\nDas ist ein'
        ' Satzglied, das die Umstände einer Handlung näher beschreibt. Die'
        ' **adverbiale Bestimmung der Zeit (Temporaladverbial)** fragt nach'
        ' **Wann?**, **Wie lange?** oder **Wie oft?**.\n*Beispiel:* „*Morgen*'
        ' fahren wir in den Urlaub.“ (Wann? -> Morgen).'
    )
  elif any(
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
          '🧮 **Wurzel & Quadrat:** Die Quadratwurzel ($\sqrt{x}$) ist die'
          ' mathematische Umkehrung zum Quadrieren ($x^2$). Beispiel:'
          ' $\sqrt{25} = 5$, da $5 \times 5 = 25$.'
      )
    return (
        '🧮 **Mathe-Assistent:** Ich helfe dir präzise bei Gleichungen,'
        ' Prozentrechnung oder geometrischen Formeln!'
    )
  elif any(
      w in msg for w in ['satzglieder', 'grammatik', 'subjekt', 'prädikat', 'wort']
  ):
    return (
        '📖 **Deutsch-Grammatik:**\n• **Subjekt (Wer-Fall):** Wer oder was tut'
        ' etwas?\n• **Prädikat (Tätigkeit):** Was tut das Subjekt?\n• **Akkusativobjekt'
        ' (Wen-Fall):** Wen oder was?\n• **Dativobjekt (Wem-Fall):** Wem?'
    )
  elif any(
      w in msg for w in ['code', 'python', 'programmieren', 'skript', 'fehler']
  ):
    return (
        '🛠️ **Code & Problemlösung:** Als dein technischer KI-Assistent analysiere'
        ' ich Code-Schnipsel, suche Logikfehler oder helfe dir beim Aufbau von'
        ' Flask- und Python-Skripten. Welches Problem möchtest du lösen?'
    )
  elif any(w in msg for w in ['hallo', 'hi', 'hey', 'moin', 'servus']):
    return (
        f'Hey {username}! 😊 Ich bin dein intelligenter Pixelcraft Solutions'
        ' KI-Assistent. Wie kann ich dir heute beim Lernen, Planen oder'
        ' Programmieren helfen?'
    )
  else:
    return (
        f'Das ist ein spannender Aspekt zu "{user_message}". Als deine'
        ' Allrounder-KI analysiere ich Zusammenhänge, helfe bei Recherchen'
        ' oder entwickle kreative Lösungen für dich. Was genau möchtest du'
        ' dazu wissen? 🤖✨'
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form.get('username', '').strip()
    contact = request.form.get('contact', '').strip()
    password = request.form.get('password', '')
    rules_accepted = request.form.get('rules_accepted')

    if not rules_accepted:
      flash('Du musst das Regelwerk und die DSGVO akzeptieren!')
      return redirect(url_for('register'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    if c.fetchone():
      flash('Benutzername bereits vergeben!')
      conn.close()
      return redirect(url_for('register'))

    hashed_pw = hash_password(password)
    c.execute(
        'INSERT INTO users (username, contact, password, roles, hide_contact)'
        ' VALUES (?, ?, ?, ?, ?)',
        (username, contact, hashed_pw, '', 0),
    )
    conn.commit()
    conn.close()

    flash(
        'Registrierung erfolgreich! Du kannst dich jetzt mit deinen Daten'
        ' anmelden.'
    )
    return redirect(url_for('login'))

  return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        'SELECT id, contact, password FROM users WHERE username = ?', (username,)
    )
    user = c.fetchone()
    conn.close()

    if user and user['password'] == hash_password(password):
      session.permanent = True
      session['username'] = username
      session['contact'] = user['contact']
      return redirect(url_for('index'))
    else:
      flash('Ungültiger Benutzername oder falsches Passwort!')

  return render_template('login.html')


@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('login'))


# 🛡️ Admin-Dashboard & Rollen-Verwaltung
@app.route('/admin-dashboard', methods=['GET', 'POST'])
def admin_dashboard():
  if 'username' not in session or not is_admin_user(session['username']):
    flash('Zugriff verwehrt! Nur für Admins.')
    return redirect(url_for('index'))

  conn = get_db_connection()
  c = conn.cursor()

  if request.method == 'POST':
    action = request.form.get('action')
    target_user = request.form.get('target_user', '').strip()

    if action == 'update_roles':
      selected_roles = request.form.getlist('roles')
      roles_str = ','.join(selected_roles)
      c.execute(
          'UPDATE users SET roles = ? WHERE username = ?',
          (roles_str, target_user),
      )
      conn.commit()
      flash(f'Rollen für "{target_user}" erfolgreich aktualisiert!')

    elif action == 'toggle_hide_contact':
      c.execute(
          'UPDATE users SET hide_contact = CASE WHEN hide_contact = 1 THEN 0'
          ' ELSE 1 END WHERE username = ?',
          (target_user,),
      )
      conn.commit()
      flash(f'Datenschutz-Status für "{target_user}" geändert.')

    elif action == 'add_admin' and target_user:
      c.execute('SELECT id FROM users WHERE username = ?', (target_user,))
      if c.fetchone():
        c.execute(
            'INSERT OR IGNORE INTO admins (username) VALUES (?)', (target_user,)
        )
        conn.commit()
        flash(f'Benutzer "{target_user}" wurde zum Admin ernannt.')
      else:
        flash(f'Benutzer "{target_user}" existiert nicht!')

    elif action == 'remove_admin' and target_user:
      if target_user.lower() == 'skyguy':
        flash('Der Haupt-Admin SkyGuy kann nicht entfernt werden!')
      elif target_user.lower() == session['username'].lower():
        flash('Du kannst dich nicht selbst als Admin entfernen!')
      else:
        c.execute('DELETE FROM admins WHERE username = ?', (target_user,))
        conn.commit()
        flash(f'Admin-Rechte für "{target_user}" entfernt.')

    return redirect(url_for('admin_dashboard'))

  c.execute('SELECT id, username, contact, roles, hide_contact FROM users')
  users_raw = c.fetchall()
  users = []
  for u in users_raw:
    user_dict = dict(u)
    user_dict['user_roles'] = [
        r.strip() for r in u['roles'].split(',') if r.strip()
    ]
    users.append(user_dict)

  c.execute('SELECT username FROM admins')
  admins = [row['username'] for row in c.fetchall()]

  conn.close()

  available_roles = [
      'CEO',
      'CTO',
      'COO',
      'Director of Development & Technical',
      'Project Lead',
      'Deputy Project Lead',
      'Operations / Community Director',
      'Business Development Manager',
      'Project Manager',
      'Product Manager',
      'Marketing & Social Media Manager',
      'Lead Developer',
      'Developer',
      'Bot Developer',
      'Script Developer',
      'UI/UX Designer',
      'QA-Tester (Quality Assurance)',
      'Cybersecurity Analyst',
      'Head Moderator',
      'Senior Moderator',
      'Moderator',
      'Jr Moderator',
      'Head Supporter',
      'Senior Supporter',
      'Supporter',
      'Community Manager',
      'Community Sprecher',
      'VIP',
      'Kunden',
  ]

  return render_template(
      'admin.html',
      users=users,
      admins=admins,
      total_users=len(users),
      current_admin=session['username'],
      available_roles=available_roles,
  )


@app.route('/', methods=['GET', 'POST'])
def index():
  if 'username' not in session:
    return redirect(url_for('login'))

  username = session['username']
  contact = session.get('contact', '')
  user_file_prefix = f'{username}_'

  if request.method == 'POST':
    action = request.form.get('action')

    if action == 'add_notiz':
      notiz = request.form.get('notiz')
      if notiz:
        with open(f'{user_file_prefix}notizen.txt', 'a', encoding='utf-8') as f:
          f.write(notiz + '\n')
    elif action == 'del_notiz':
      idx = request.form.get('index')
      if idx is not None:
        idx = int(idx)
        fpath = f'{user_file_prefix}notizen.txt'
        if os.path.exists(fpath):
          with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
          if 0 <= idx < len(lines):
            lines.pop(idx)
            with open(fpath, 'w', encoding='utf-8') as f:
              f.writelines(lines)
    elif action == 'add_einkauf':
      item = request.form.get('einkauf_item')
      menge = request.form.get('einkauf_menge', '1')
      if item:
        with open(f'{user_file_prefix}einkauf.txt', 'a', encoding='utf-8') as f:
          f.write(f'{item} (Anzahl: {menge})\n')
    elif action == 'del_einkauf':
      idx = request.form.get('index')
      if idx is not None:
        idx = int(idx)
        fpath = f'{user_file_prefix}einkauf.txt'
        if os.path.exists(fpath):
          with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
          if 0 <= idx < len(lines):
            lines.pop(idx)
            with open(fpath, 'w', encoding='utf-8') as f:
              f.writelines(lines)
    elif action == 'add_note':
      fach = request.form.get('fach')
      note = request.form.get('note')
      if fach and note:
        with open(f'{user_file_prefix}noten.txt', 'a', encoding='utf-8') as f:
          f.write(f'{fach}:{note}\n')
    elif action == 'del_note':
      idx = request.form.get('index')
      if idx is not None:
        idx = int(idx)
        fpath = f'{user_file_prefix}noten.txt'
        if os.path.exists(fpath):
          with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
          if 0 <= idx < len(lines):
            lines.pop(idx)
            with open(fpath, 'w', encoding='utf-8') as f:
              f.writelines(lines)
    elif action == 'add_vokabel':
      de = request.form.get('deutsch')
      fr = request.form.get('fremd')
      if de and fr:
        with open(f'{user_file_prefix}vokabeln.txt', 'a', encoding='utf-8') as f:
          f.write(f'{de} = {fr}\n')
    elif action == 'del_vokabel':
      idx = request.form.get('index')
      if idx is not None:
        idx = int(idx)
        fpath = f'{user_file_prefix}vokabeln.txt'
        if os.path.exists(fpath):
          with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
          if 0 <= idx < len(lines):
            lines.pop(idx)
            with open(fpath, 'w', encoding='utf-8') as f:
              f.writelines(lines)
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
  vokabeln_liste = read_file(f'{user_file_prefix}vokabeln.txt')

  noten_roh = read_file(f'{user_file_prefix}noten.txt')
  noten_liste = []
  summe = 0
  anzahl = 0
  for line in noten_roh:
    if ':' in line:
      teile = line.split(':')
      fach = teile[0]
      try:
        note_val = float(teile[1])
        noten_liste.append({'fach': fach, 'note': note_val})
        summe += note_val
        anzahl += 1
      except ValueError:
        pass

  schnitt = round(summe / anzahl, 2) if anzahl > 0 else 0.0
  is_admin = is_admin_user(username)

  return render_template(
      'index.html',
      username=username,
      notizen=notizen,
      einkauf_liste=einkauf_liste,
      chats=chats,
      noten_liste=noten_liste,
      schnitt=schnitt,
      vokabeln_liste=vokabeln_liste,
      is_admin=is_admin,
  )


if __name__ == '__main__':
  app.run(debug=True)
