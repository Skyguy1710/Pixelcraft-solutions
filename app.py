import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'Pixelcraft Solution1710'

# Hilfsfunktion: Stellt sicher, dass alle benötigten Textdateien existieren
def check_files():
    files = ['benutzer.txt', 'notizen.txt', 'chats.txt']
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w', encoding='utf-8') as f:
                f.write('')  # Erstellt eine leere Datei, falls sie fehlt

@app.route('/')
def home():
    check_files()  # Dateien vor dem Laden absichern
    try:
        # Hier landet dein normaler Startseiten-Code (z.B. Login oder Index)
        return render_template('login.html')
    except Exception as e:
        return f"Ein Fehler ist aufgetreten: {str(e)}", 500

# Falls du weitere Routen hast (z.B. für Login, Registrierung oder Chats), 
# füge sie einfach hier darunter ein und achte darauf, überall 
# open(..., encoding='utf-8') zu verwenden.

if __name__ == '__main__':
    app.run(debug=True)