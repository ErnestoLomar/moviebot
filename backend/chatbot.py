import logging
import re
from llm_agent import analyze_message, suggest_movie_titles, build_intro_with_movies, llm_reply_from_context
from movie_api import get_movie_by_title

class Chatbot:
    def __init__(self):
        self.sessions = {}
        self.histories = {}
        self.question_counters = {}
        
    def init_session(self, session_id):
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
            self.histories[session_id] = []
            self.question_counters[session_id] = 0
            
    def limpiar_titulo(self, titulo):
        # Elimina paréntesis y su contenido
        return re.sub(r"\s*\([^)]*\)", "", titulo).strip()

    def handle_message(self, message, session_id):
        try:
            self.init_session(session_id)

            self.question_counters[session_id] += 1
            history = self.histories[session_id]
            history.append({"role": "user", "content": message})
            
            logging.info(f"[{session_id}] Usuario: {message}")

            analysis = analyze_message(history)
            self.sessions[session_id]["last_analysis"] = analysis
            logging.info(f"[{session_id}] Análisis: {analysis}")

            if not analysis.get('is_movie_related', False):
                reply = analysis.get("mensaje", "¿Sobre qué género de películas quieres hablar?")
                history.append({"role": "assistant", "content": reply})
                logging.info(f"[{session_id}] Bot (tema no válido): {reply}")
                return {
                    "reply": reply,
                    "movies": [],
                    "question_count": self.question_counters[session_id]
                }

            try:
                titles = suggest_movie_titles(message, analysis)[:5]
                logging.info(f"[{session_id}] Títulos sugeridos: {titles}")
            except Exception as e:
                logging.exception(f"[{session_id}] Error al sugerir títulos")
                titles = []
                
            movies = []
            for title in titles:
                try:
                    titulo_limpio = self.limpiar_titulo(title)
                    movie = get_movie_by_title(titulo_limpio)
                    if movie:
                        movies.append(movie)
                    else:
                        fallback_movie = {
                            "title": title,
                            "year": analysis.get("year", ""),
                            "genre": analysis.get("genre", "desconocido"),
                            "overview": "No se encontró una sinopsis, pero esta película fue recomendada por el asistente.",
                            "actors": ["No disponible"]
                        }
                        logging.warning(f"[{session_id}] Usando fallback para: {title}")
                        movies.append(fallback_movie)
                except Exception as e:
                    logging.exception(f"[{session_id}] Error al obtener película: {title}")
            movies = movies[:5]

            if not movies:
                reply = "No pude encontrar películas que coincidan en este momento. ¿Quieres probar con otro género o saga?"
                history.append({"role": "assistant", "content": reply})
                logging.warning(f"[{session_id}] Bot (sin resultados): {reply}")
                return {
                    "reply": reply,
                    "movies": [],
                    "question_count": self.question_counters[session_id]
                }

            try:
                intro = build_intro_with_movies(movies, analysis.get("genre") or analysis.get("franchise"))
                reply = llm_reply_from_context(message, intro)
            except Exception as e:
                logging.exception(f"[{session_id}] Error al generar respuesta con LLM")
                reply = "Aquí tienes algunas películas que pueden interesarte."
                
            history.append({"role": "assistant", "content": reply})
            logging.info(f"[{session_id}] Bot: {reply}")

            return {
                "reply": reply,
                "movies": movies,
                "question_count": self.question_counters[session_id]
            }
            
        except Exception as e:
            logging.exception(f"[{session_id}] Error general en handle_message")
            return {
                "reply": "Lo siento, ocurrió un error interno. ¿Puedes intentar de nuevo?",
                "movies": [],
                "question_count": self.question_counters.get(session_id, 0)
            }