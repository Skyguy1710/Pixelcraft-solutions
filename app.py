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
  msg_lower = user_message.lower()

  # Zusammenfassungs- & Schul-Helfer
  if 'zusammenfassen' in msg_lower or 'zusammenfassung' in msg_lower:
    return (
        '📚 **Lern-Zusammenfassung:** Hier sind die wichtigsten Punkte kurz'
        ' für deine Klausur auf den Punkt gebracht:\n1. Konzentriere dich auf'
        ' das Wesentliche.\n2. Nutze Schlüsselbegriffe.\n3. Mach regelmäßige'
        ' Pausen! Du packst das! 🚀'
    )

  elif 'formel' in msg_lower or 'grammatik' in msg_lower:
    return (
        '💡 **Wissens-Schatzkiste:** Wenn du eine spezifische Matheformel oder'
        ' eine Grammatikregel (z.B. Subjekt, Prädikat, Objekt) brauchst,'
        ' schreib mir einfach das Thema und ich erkläre es dir kinderleicht!'
    )

  # Einkaufs-Logik im Chat
  elif 'einkauf' in msg_lower or 'kaufen' in msg_lower:
    return (
        'Schreib es am besten direkt in die Einkaufsliste, damit du es im'
        ' Supermarkt parat hast! 🛒'
    )

  # Sympathische Begrüßungen & Smalltalk
  elif any(
      w in msg_lower
      for w in ['hallo', 'hi', 'hey', 'moin', 'guten tag', 'servus']
  ):
    return (
        'Hey! 😊 Schön, dass du da bist. Was lernen wir heute oder was steht'
        ' bei dir an?'
    )

  elif 'wie geht es dir' in msg_lower or 'wie gehts' in msg_lower:
    return (
        'Mir geht es ausgezeichnet! Bereit, dir den Lerntag zu erleichtern. 🚀'
        ' Und bei dir alles fit?'
    )

  elif 'wer bist du' in msg_lower or 'was kannst du' in msg_lower:
    return (
        'Ich bin dein smarter KI-Assistent von Pixelcraft Solutions! Ich helfe'
        ' dir bei Notizen, fasse Texte für die Schule zusammen und quatsche'
        ' auch gerne mit dir.'
    )

  else:
    return (
        f'Das ist ein spannender Punkt: "{user_message}". Erzähl mir gerne'
        ' mehr oder frag mich, wenn du eine Zusammenfassung brauchst!'
    )


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    if 'notiz' in request.form:
      notiz = request.form.get('notiz')
      if notiz:
        with open('notizen.txt', 'a', encoding='utf-8') as f:
          f.write(notiz + '\n')
    elif 'einkauf_item' in request.form:
      einkauf = request.form.get('einkauf_item')
      if einkauf:
        with open('einkauf.txt', 'a', encoding='utf-8') as f:
          f.write(einkauf + '\n')
    elif 'nachricht' in request.form:
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