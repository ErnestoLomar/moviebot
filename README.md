# 🎬 MovieBot – Asistente de Recomendación de Películas

**MovieBot** es un chatbot inteligente especializado en recomendar películas en español utilizando modelos de lenguaje (LLM) de OpenAI y la API de [TMDb](https://www.themoviedb.org/). El asistente conversa con el usuario de forma natural y cálida, comprendiendo géneros, actores, franquicias o tipos de películas solicitadas, y sugiere títulos relevantes con sinopsis y actores principales.

---

## 🧠 Funcionalidades

- ✅ Entendimiento de lenguaje natural (gracias a GPT-4.1).
- 🎞️ Análisis semántico del mensaje para extraer género, franquicia, año, actor, etc.
- 🎬 Consulta de películas reales desde la API de TMDb.
- 🗣️ Generación de respuestas conversacionales, amigables y sin listas.
- 📚 Contexto de conversación por sesión.
- 🔁 Reintentos elegantes cuando no hay resultados.
- 🧰 Fallback automático cuando no se encuentra una película en la API.
- 📦 Modularizado y fácil de extender.

---

## 📁 Estructura del proyecto

```
moviebot/
│
├── chatbot.py               # Controlador principal de la conversación
├── llm_agent.py             # Interacción con el modelo de lenguaje (GPT)
├── movie_api.py             # Acceso a TMDb (búsquedas por título, género, actor)
├── .env                     # Variables de entorno (API Keys)
├── requirements.txt         # Dependencias del proyecto
└── app.py (opcional)       # Servidor web local para pruebas (Flask/FastAPI)
```

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/ErnestoLomar/moviebot.git
cd moviebot
```

### 2. Crear entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
source venv/bin/activate  # en Linux/macOS
venv\Scripts\activate     # en Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar `.env`

Crea un archivo `.env` en la raíz del proyecto y coloca:

```
OPENAI_API_KEY=tu_clave_de_openai
TMDB_API_KEY=tu_clave_de_tmdb
```

Puedes obtener tu API key de:

- [OpenAI](https://platform.openai.com/account/api-keys)
- [TMDb](https://www.themoviedb.org/settings/api)

---

## 🚀 Uso

Puedes probar el bot desde un archivo `app.py` con Flask/FastAPI o desde consola importando `Chatbot`.

### Desde consola:

```python
from chatbot import Chatbot

bot = Chatbot()
session_id = "usuario1"

while True:
    user_input = input("Tú: ")
    response = bot.handle_message(user_input, session_id)
    print("\nMovieBot:", response["reply"])
```

### Desde un servidor web (ejemplo mínimo con Flask):

```python
# app.py
from flask import Flask, request, jsonify
from chatbot import Chatbot

app = Flask(__name__)
bot = Chatbot()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data["message"]
    session_id = data["session_id"]
    response = bot.handle_message(message, session_id)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
```

---

## 📦 Requisitos

```
openai
langchain
langchain-openai
python-dotenv
requests
flask
```

Guárdalos en `requirements.txt`:

```
openai
langchain
langchain-openai
python-dotenv
requests
flask
```

---

## 🔍 Ejemplos para testear

- "¿Qué películas me recomiendas de terror psicológico?"
- "Quiero ver algo con Ryan Gosling"
- "¿Películas de Marvel?"
- "Dame comedias románticas modernas"
- "Busco un drama del 2010"
- "¿Recomiendas alguna de ciencia ficción con viajes en el tiempo?"

---

## 🔧 Mejoras implementadas

- ✅ Limpieza de títulos con paréntesis y subtítulos.
- ✅ Fallback con título manual si no se encuentra en TMDb.
- ✅ Traducción automática de género al formato de TMDb.
- ✅ Manejo de errores robusto y logs por sesión.

---

## 🤝 Créditos

- [OpenAI](https://openai.com/)
- [TMDb API](https://www.themoviedb.org/)

---

## 🛡️ Licencia

Este proyecto está licenciado bajo la **MIT License**.