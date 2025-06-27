from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from chatbot import Chatbot

app = Flask(__name__)
CORS(app)

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

chatbot = Chatbot()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({"error": "El mensaje no puede estar vacío."}), 400

        response = chatbot.handle_message(user_message, session_id)
        return jsonify(response)
    except Exception as e:
        logging.exception("Error en el endpoint /chat")
        return jsonify({"error": "Error interno del servidor."}), 500

if __name__ == '__main__':
    app.run(debug=True)