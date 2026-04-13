from flask import Flask, render_template, request, jsonify, send_file
from groq import Groq
from gtts import gTTS
import os
import io
import base64

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

konusma_gecmisi = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sohbet", methods=["POST"])
def sohbet():
    data = request.json
    mesaj = data.get("mesaj", "")
    sesli = data.get("sesli", False)

    konusma_gecmisi.append({"role": "user", "content": mesaj})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Sen yardımcı bir yapay zeka asistanısın. Türkçe konuş, kısa ve net cevaplar ver."}
        ] + konusma_gecmisi,
        max_tokens=500
    )

    cevap = response.choices[0].message.content
    konusma_gecmisi.append({"role": "assistant", "content": cevap})

    ses_base64 = None
    if sesli:
        tts = gTTS(text=cevap, lang="tr")
        ses_io = io.BytesIO()
        tts.write_to_fp(ses_io)
        ses_io.seek(0)
        ses_base64 = base64.b64encode(ses_io.read()).decode("utf-8")

    return jsonify({"cevap": cevap, "ses": ses_base64})

@app.route("/temizle", methods=["POST"])
def temizle():
    global konusma_gecmisi
    konusma_gecmisi = []
    return jsonify({"durum": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
