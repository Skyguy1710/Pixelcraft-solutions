import os
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = 'Pixelcraft Solution1710'


def check_files():
  for filename in ['notizen.txt', 'chats.txt', 'einkauf.txt']:
    if not os.path.exists(filename):
      with open(filename, 'w', encoding='utf-8') as f:
        f.write('')


check_files()


def generate_ai_response(user_message):
  msg = user_message.lower()

  # Mathe-Logik
  if (
      any(op in msg for op in ['+', '-', '*', '/', 're("*", msg)'])
      or 'was ist' in msg
      or 'wieviel' in msg
      or 'mathe' in msg
  ):
    try:
      # Einfache Mathe-Auswertung falls Zahlen enthalten sind
      clean_msg = (
          msg.replace('was ist', '')
          .replace('wieviel ist', '')
          .replace('?', '')
          .strip()
      )
      if any(c.isdigit() for c in clean_msg):
        result = eval(clean_msg)
        return f'🧮 Mathe-Ergebnis: {clean_msg} = {result}!'
    except:
      pass
    return (
        '🧮 **Mathe-Hilfe:** Ich kann rechnen, Formeln erklären (z.B. Satz des'
        ' Pythagoras) oder dir bei Gleichungen helfen! Was brauchst du?'
    )

  # Grammatik & Satzglieder
  elif (
      'satzglieder' in msg
      or 'grammatik' in msg
      or 'subjekt' in msg
      or 'prädikat' in msg
  ):
    return (
        '📖 **Deutsch & Grammatik:**\n• **Subjekt** (Wer oder was? Nominativ)\n•'
        ' **Prädikat** (Was tut das Subjekt? Verb)\n• **Akkusativobjekt** (Wen'
        ' oder was?)\n• **Dativobjekt** (Wem?)\nMit der Umstellprobe kannst du'
        ' sie im Satz verschieben!'
    )

  # Zusammenfassung
  elif 'zusammenfassen' in msg or 'zusammenfassung' in msg or 'fass' in msg:
    return (
        '📚 **Zusammenfassung:** Hier sind die Kernpunkte:\n1. Konzentriere dich'
        ' auf das Wesentliche.\n2. Nutze Schlüsselbegriffe.\n3. Wiederhole den'
        ' Stoff regelmäßig. Du packst das! 🚀'
    )

  # Begrüßung
  elif any(w in msg for w in ['hallo', 'hi', 'hey', 'moin', 'servus']):
    return (
        'Hey! 😊 Schön, dass du da bist. Wie kann ich dir heute bei der Schule'
        ' oder deinen Projekten helfen?'
    )

  else:
    return (
        f'Das ist eine spannende Frage zu "{user_message}"! Als dein'
        ' KI-Assistent helfe ich dir bei Mathe, Grammatik, Notizen und'
        ' vielem mehr. Frag mich einfach gezielt danach! 🤖'
    )


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    action = request.form.get('action')

    if action == 'add_notiz':
      notiz = request.form.get('notiz')
      if notiz:
        with open('notizen.txt', 'a', encoding='utf-8') as f:
          f.write(notiz + '\n')
    elif action == 'del_notiz':
      idx = int(request.form.get('index'))
      if os.path.exists('notizen.txt'):
        with open('notizen.txt', 'r', encoding='utf-8') as f:
          lines = f.readlines()
        if 0 <= idx < len(lines):
          lines.pop(idx)
          with open('notizen.txt', 'w', encoding='utf-8') as f:
            f.writelines(lines)

    elif action == 'add_einkauf':
      item = request.form.get('einkauf_item')
      menge = request.form.get('einkauf_menge', '1')
      if item:
        with open('einkauf.txt', 'a', encoding='utf-8') as f:
          f.write(f'{item} (Anzahl: {menge})\n')
    elif action == 'del_einkauf':
      idx = int(request.form.get('index'))
      if os.path.exists('einkauf.txt'):
        with open('einkauf.txt', 'r', encoding='utf-8') as f:
          lines = f.readlines()
        if 0 <= idx < len(lines):
          lines.pop(idx)
          with open('einkauf.txt', 'w', encoding='utf-8') as f:
            f.writelines(lines)

    elif action == 'send_chat':
      nachricht = request.form.get('nachricht')
      if nachricht:
        with open('chats.txt', 'a', encoding='utf-8') as f:
          f.write(f'Du: {nachricht}\n')
        ai_reply = generate_ai_response(nachricht)
        with open('chats.txt', 'a', encoding='utf-8') as f:
          f.write(f'KI: {ai_reply}\n')

    return redirect(url_for('index'))

  notizen = []
  if os.path.exists('notizen.txt'):
    with open('notizen.txt', 'r', encoding='utf-8') as f:
      notizen = [line.strip() for line in f.readlines()]

  einkauf_liste = []
  if os.path.exists('einkauf.txt'):
    with open('einkauf.txt', 'r', encoding='utf-8') as f:
      einkauf_liste = [line.strip() for line in f.readlines()]

  chats = []
  if os.path.exists('chats.txt'):
    with open('chats.txt', 'r', encoding='utf-8') as f:
      chats = [line.strip() for line in f.readlines()]

  return render_template(
      'index.html',
      notizen=notizen,
      einkauf_liste=einkauf_liste,
      chats=chats,
  )


if __name__ == '__main__':
  app.run(debug=True)
