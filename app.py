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


@app.route('/', methods=['GET', 'POST'])
def index():
  try:
    if request.method == 'POST':
      if 'notiz' in request.form:
        notiz = request.form.get('notiz')
        if notiz:
          with open('notizen.txt', 'a', encoding='utf-8') as f:
            f.write(notiz + '\n')
      elif 'nachricht' in request.form:
        nachricht = request.form.get('nachricht')
        if nachricht:
          with open('chats.txt', 'a', encoding='utf-8') as f:
            f.write(nachricht + '\n')
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
  except Exception as e:
    # Zeigt den echten Python-Fehler direkt im Browser an, statt abzustürzen
    return f'FEHLER: {str(e)}'


if __name__ == '__main__':
    app.run(debug=True)