import os
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = 'Pixelcraft Solution1710'


def check_files():
  for filename in ['notizen.txt', 'chats.txt']:
    if not os.path.exists(filename):
      with open(filename, 'w', encoding='utf-8') as f:
        f.write('')


check_files()


def generate_ai_response(user_message):
  msg_lower = user_message.lower()

  # Erinnerungs-Logik
  if 'erinnerung' in msg_lower or 'erinnere' in msg_lower:
    return (
        f'Erinnerung erfolgreich gespeichert! Ich werde dich erinnern:'
        f' "{user_message}" 🤖'
    )

  # Wissen / Fragen beantworten (z.B. Satzglieder)
  elif 'satzglieder' in msg_lower:
    return (
        'Satzglieder sind die Bausteine eines Satzes (z.B. Subjekt, Prädikat,'
        ' Objekt). Sie lassen sich im Satz verschieben (Umstellprobe).'
    )

  elif 'hallo' in msg_lower or 'hi' in msg_lower:
    return (
        'Hallo! Ich bin deine Pixelcraft AI. Wie kann ich dir heute helfen?'
    )

  else:
    return (
        f'Das habe ich verstanden: "{user_message}". Als KI-Assistent von'
        ' Pixelcraft Solutions stehe ich dir bei Notizen und Organisation zur'
        ' Seite!'
    )


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    if 'notiz' in request.form:
      notiz = request.form.get('notiz')
      if notiz:
        with open('notizen.txt', 'a', encoding='utf-8') as f:
          f.write(notiz + '\n')
    elif 'nachricht' in request.form:
      nachricht = request.form.get('nachricht')
      if nachricht:
        # Benutzer-Nachricht speichern
        with open('chats.txt', 'a', encoding='utf-8') as f:
          f.write(f'Du: {nachricht}\n')
        # KI-Antwort generieren und speichern
        ai_reply = generate_ai_response(nachricht)
        with open('chats.txt', 'a', encoding='utf-8') as f:
          f.write(f'KI: {ai_reply}\n')

    return redirect(url_for('index'))

  notizen = []
  if os.path.exists('notizen.txt'):
    with open('notizen.txt', 'r', encoding='utf-8') as f:
      notizen = [line.strip() for line in f.readlines()]

  chats = []
  if os.path.exists('chats.txt'):
    with open('chats.txt', 'r', encoding='utf-8') as f:
      chats = [line.strip() for line in f.readlines()]

  return render_template('index.html', notizen=notizen, chats=chats)


if __name__ == '__main__':
  app.run(debug=True)