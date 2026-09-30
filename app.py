import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from chatbot_config import SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.6-flash"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=API_KEY)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"reply": "Please enter a message you want help with."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"{SYSTEM_PROMPT}\n\nUser request:\n{message}"
        )
        reply = response.text or "I couldn't create a rewrite. Please try again."
        return jsonify({"reply": reply})
    except Exception as error:
        app.logger.exception("Gemini API error: %s", error)
        return jsonify({
            "reply": "I’m having trouble connecting right now. Please try again in a moment."
        }), 500

if __name__ == "__main__":
    app.run()
