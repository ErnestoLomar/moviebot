import os
import json
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Cargar variables de entorno
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """
    Eres un asistente conversacional experto en recomendaciones de películas.

    Tu único propósito es hablar sobre cine, películas, actores, géneros, sagas, directores, etc.

    No debes responder preguntas fuera de ese ámbito. Si el usuario pide ayuda sobre otro tema (por ejemplo, teléfonos, computadoras, recetas, etc.), debes rechazarlo amablemente y recordarle que solo puedes hablar de películas.

    Tu respuesta debe ser un JSON con la siguiente estructura:

    {
        "is_movie_related": true/false,
        "genre": "...",
        "year": "...",
        "actor": "...",
        "franchise": "...",
        "detail_request": "...",
        "movie_title": "...",
        "mensaje": "..."  // mensaje amigable y útil para el usuario, que invite a seguir hablando de cine
    }

    No inventes respuestas fuera del tema de películas. Sé educado, pero firme.
"""

def analyze_message(history):
    try:
        response = llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            *history
        ])
        content = response.content.strip().replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
        
        logging.info("Análisis recibido del LLM.")
        logging.debug(f"Contenido bruto: {content}")
        
        if content.startswith("{"):
            return json.loads(content)
        else:
            logging.warning("Respuesta del LLM no es JSON.")
            return {}
    except json.JSONDecodeError:
        logging.exception("Error al decodificar JSON en analyze_message.")
        return {}
    except Exception:
        logging.exception("Error general en analyze_message.")
        return {}

def build_intro_with_movies(movies, context_label):
    titles = [m['title'] for m in movies[:5]]
    prompt = f"""
            Eres un experto en cine. El usuario ha pedido recomendaciones y tienes estas películas: {titles}.
            Redacta una introducción amigable, cálida y sin usar listas ni mencionar títulos específicos.
            Habla del tipo de películas, no de sus nombres. Evita enumerar o listar.
        """
    try:
        response = llm.invoke([{"role": "system", "content": prompt}])
        logging.info("Intro generada correctamente.")
        return response.content.strip()
    except:
        logging.exception("Error al construir la introducción con películas.")
        return "Aquí tienes algunas recomendaciones."

def llm_reply_from_context(user_input, intro):
    prompt = f"""
            Eres un asistente especializado en películas. El usuario dijo:
            "{user_input}"

            Esta es la introducción a las películas recomendadas:
            "{intro}"

            Responde de forma natural, cálida y conversacional. No repitas los títulos. No uses listas ni números. Incluye emojis si lo consideras útil.
            Devuelve solo el texto.
        """
    try:
        response = llm.invoke([{"role": "system", "content": prompt}])
        logging.info("Respuesta generada desde contexto.")
        return response.content.strip()
    except:
        logging.exception("Error en llm_reply_from_context.")
        return intro

def suggest_movie_titles(user_input, analysis):
    prompt = f"""
            Eres un sistema experto en películas. El usuario dijo:
            "{user_input}"

            Y el análisis estructurado es:
            {json.dumps(analysis, indent=2)}

            Basado en eso, sugiere entre 3 y 5 títulos de películas reales que podrían gustarle (devuélvelas como lista JSON). No escribas nada más.
        """
    try:
        response = llm.invoke([{"role": "system", "content": prompt}])
        raw = response.content.strip()
        logging.info("Títulos sugeridos generados.")
        return json.loads(raw)[:5] if raw.startswith("[") else []
    except json.JSONDecodeError:
        logging.warning("Respuesta de títulos sugeridos no es JSON.")
        return []
    except Exception as e:
        logging.exception("Error en suggest_movie_titles.")
        return []