# Pixelcraft Solutions - Login, Notizen & Erweiterter AI-Chat
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
import re
from plyer import notification

app = Flask(__name__)
app.secret_key = "pixelcraft_secure_key"

DATEI_NOTIZEN = "notizen.txt"
DATEI_CHATS = "chats.txt"
DATEI_BENUTZER = "benutzer.txt"

def daten_laden(datei):
    if not os.path.exists(datei):
        return []
    with open(datei, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]

def daten_speichern(datei, daten):
    with open(datei, "w", encoding="utf-8") as file:
        for eintrag in daten:
            file.write(f"{eintrag}\n")

def ki_antwort_generieren(frage):
    """Die PCS-KI für Mathe, Coding und allgemeine Fragen"""
    frage_lower = frage.lower()
    
    match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)', frage)
    if match:
        num1, op, num2 = match.groups()
        expr = f"{num1} {op} {num2}"
        try:
            ergebnis = eval(expr)
            return f"🤖 PCS-AI: Das Ergebnis von {expr} ist **{ergebnis}**!"
        except:
            pass

    if "hallo" in frage_lower or "hi" in frage_lower:
        return "🤖 PCS-AI: Hallo! Schön, dass du eingeloggt bist. Wie kann ich dir heute bei Pixelcraft Solutions helfen?"
    elif "wie geht" in frage_lower:
        return "🤖 PCS-AI: Mir geht es fantastisch als dein persönlicher Co-Pilot! Und dir?"
    elif "code" in frage_lower or "python" in frage_lower:
        return "🤖 PCS-AI: Programmier-Tipp: Achte immer auf saubere Einrückungen und teste deinen Code Schritt für Schritt."
    elif "erinnerung" in frage_lower or ":" in frage:
        return "🤖 PCS-AI: Erinnerung erfolgreich im 24-Stunden-Format registriert! Die Windows-Benachrichtigung wurde ausgelöst."
    else:
        return f"🤖 PCS-AI: Das ist eine interessante Frage zu '{frage}'. Ich analysiere das: Konzentriere dich auf dein Ziel, du machst das großartig!"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        passwort = request.form.get("passwort")
        if email and passwort:
            benutzer = daten_laden(DATEI_BENUTZER)
            if email not in benutzer:
                benutzer.append(email)
                daten_speichern(DATEI_BENUTZER, benutzer)
            
            session["user"] = email
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    notizen = daten_laden(DATEI_NOTIZEN)
    chats = daten_laden(DATEI_CHATS)
    return render_template("index.html", notizen=notizen, chats=chats, anzahl=len(notizen), user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/hinzufuegen_notiz", methods=["POST"])
def hinzufuegen_notiz():
    if "user" not in session:
        return redirect(url_for("login"))
    text = request.form.get("notiz")
    if text and text.strip() != "":
        jetzt = datetime.now().strftime("%d.%m.%Y %H:%M")
        eintrag = f"{text.strip()} (🕒 {jetzt})"
        notizen = daten_laden(DATEI_NOTIZEN)
        notizen.append(eintrag)
        daten_speichern(DATEI_NOTIZEN, notizen)
    return redirect(url_for("dashboard"))

@app.route("/loeschen_notiz/<int:index>")
def loeschen_notiz(index):
    notizen = daten_laden(DATEI_NOTIZEN)
    if 0 <= index < len(notizen):
        notizen.pop(index)
        daten_speichern(DATEI_NOTIZEN, notizen)
    return redirect(url_for("dashboard"))

@app.route("/chat_senden", methods=["POST"])
def chat_senden():
    if "user" not in session:
        return redirect(url_for("login"))
    nachricht = request.form.get("nachricht")
    if nachricht and nachricht.strip() != "":
        antwort = ki_antwort_generieren(nachricht)
        
        if re.search(r'\d{1,2}:\d{2}', nachricht) or "erinnerung" in nachricht.lower():
            try:
                notification.notify(
                    title="Pixelcraft Solutions KI-Erinnerung",
                    message=f"Erinnerung: {nachricht}",
                    timeout=10
                )
            except Exception as e:
                print(f"Benachrichtigungs-Fehler: {e}")

        chats = daten_laden(DATEI_CHATS)
        chats.append(f"Du: {nachricht}")
        chats.append(antwort)
        daten_speichern(DATEI_CHATS, chats)
        
    return redirect(url_for("dashboard"))

@app.route("/chat_leeren")
def chat_leeren():
    if os.path.exists(DATEI_CHATS):
        os.remove(DATEI_CHATS)
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)