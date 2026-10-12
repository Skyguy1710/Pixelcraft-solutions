import os
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = 'Pixelcraft Solution1710'


def check_files():
  for filename in [
      'notizen.txt',
      'chats.txt',
      'einkauf.txt',
      'noten.txt',
      'vokabeln.txt',
  ]:
    if not os.path.exists(filename):
      with open(filename, 'w', encoding='utf-8') as f:
        f.write('')


check_files()


def generate_ai_response(user_message):
  msg = user_message.lower()

  # Mathe-Logik
  if (
      any(op in msg for op in ['+', '-', '*', '/'])
      or 'was ist' in msg
      or 'wieviel' in msg
      or 'mathe' in msg
  ):
    try:
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
        '🧮 **Mathe-Hilfe:** Ich kann rechnen oder dir Formeln aus dem Lexikon'
        ' erklären! Was brauchst du?'
    )

  # Grammatik & Deutsch
  elif (
      'satzglieder' in msg
      or 'grammatik' in msg
      or 'subjekt' in msg
      or 'prädikat' in msg
  ):
    return (
        '📖 **Deutsch & Grammatik:**\n• **Subjekt** (Wer oder was?)\n•'
        ' **Prädikat** (Was tut das Subjekt?)\n• **Objekt** (Wen/Was oder'
        ' Wem?)\nNutze im Dashboard auch unser neues Schul-Lexikon!'
    )

  # Zusammenfassungen
  elif 'zusammenfassen' in msg or 'zusammenfassung' in msg or 'fass' in msg:
    return (
        '📚 **Zusammenfassung:** Hier sind die Kernpunkte:\n1. Konzentriere dich'
        ' auf das Wesentliche.\n2. Lerne mit den neuen Vokabel-Karteikarten!\n3.'
        ' Halte deine Noten im Notenrechner im Blick. 🚀'
    )

  # Begrüßung
  elif any(w in msg for w in ['hallo', 'hi', 'hey', 'moin', 'servus']):
    return (
        'Hey! 😊 Schön, dass du da bist. Schau dir unbedingt den neuen'
        ' Notenrechner und den Vokabeltrainer an!'
    )

  else:
    return (
        f'Das ist ein spannendes Thema zu "{user_message}"! Als dein'
        ' KI-Assistent helfe ich dir bei Mathe, Grammatik, Vokabeln und Noten.'
        ' Frag mich einfach gezielt danach! 🤖'
    )


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    action = request.form.get('action')

    # Notizen
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

    # Einkaufsliste
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

    # Notenrechner
    elif action == 'add_note':
      fach = request.form.get('fach')
      note = request.form.get('note')
      if fach and note:
        with open('noten.txt', 'a', encoding='utf-8') as f:
          f.write(f'{fach}: {note}\n')
    elif action == 'del_note':
      idx = int(request.form.get('index'))
      if os.path.exists('noten.txt'):
        with open('noten.txt', 'r', encoding='utf-8') as f:
          lines = f.readlines()
        if 0 <= idx < len(lines):
          lines.pop(idx)
          with open('noten.txt', 'w', encoding='utf-8') as f:
            f.writelines(lines)

    # Vokabeltrainer
    elif action == 'add_vokabel':
      wort = request.form.get('wort')
      uebersetzung = request.form.get('uebersetzung')
      if wort and uebersetzung:
        with open('vokabeln.txt', 'a', encoding='utf-8') as f:
          f.write(f'{wort}|{uebersetzung}\n')
    elif action == 'del_vokabel':
      idx = int(request.form.get('index'))
      if os.path.exists('vokabeln.txt'):
        with open('vokabeln.txt', 'r', encoding='utf-8') as f:
          lines = f.readlines()
        if 0 <= idx < len(lines):
          lines.pop(idx)
          with open('vokabeln.txt', 'w', encoding='utf-8') as f:
            f.writelines(lines)

    # AI Chat
    elif action == 'send_chat':
      nachricht = request.form.get('nachricht')
      if nachricht:
        with open('chats.txt', 'a', encoding='utf-8') as f:
          f.write(f'Du: {nachricht}\n')
        ai_reply = generate_ai_response(nachricht)
        with open('chats.txt', 'a', encoding='utf-8') as f:
          f.write(f'KI: {ai_reply}\n')

    return redirect(url_for('index'))

  # Daten laden
  notizen = []
  if os.path.exists('notizen.txt'):
    with open('notizen.txt', 'r', encoding='utf-8') as f:
      notizen = [line.strip() for line in f.readlines()]

  einkauf_liste = []
  if os.path.exists('einkauf.txt'):
    with open('einkauf.txt', 'r', encoding='utf-8') as f:
      einkauf_liste = [line.strip() for line in f.readlines()]

  noten_liste = []
  noten_summe = 0
  if os.path.exists('noten.txt'):
    with open('noten.txt', 'r', encoding='utf-8') as f:
      for line in f.readlines():
        line = line.strip()
        if line:
          noten_liste.append(line)
          try:
            val = float(line.split(': ')[1])
            noten_summe += val
          except:
            pass

  schnitt = (
      round(noten_summe / len(noten_liste), 2) if len(noten_liste) > 0 else 0.0
  )

  vokabeln_liste = []
  if os.path.exists('vokabeln.txt'):
    with open('vokabeln.txt', 'r', encoding='utf-8') as f:
      for line in f.readlines():
        line = line.strip()
        if '|' in line:
          w, u = line.split('|', 1)
          vokabeln_liste.append({'wort': w, 'uebersetzung': u})

  chats = []
  if os.path.exists('chats.txt'):
    with open('chats.txt', 'r', encoding='utf-8') as f:
      chats = [line.strip() for line in f.readlines()]

  return render_template(
      'index.html',
      notizen=notizen,
      einkauf_liste=einkauf_liste,
      noten_liste=noten_liste,
      schnitt=schnitt,
      vokabeln_liste=vokabeln_liste,
      chats=chats,
  )


if __name__ == '__main__':
  app.run(debug=True)
