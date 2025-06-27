import requests
import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
GENRES = {
    "acción": 28,
    "aventura": 12,
    "animación": 16,
    "comedia": 35,
    "crimen": 80,
    "documental": 99,
    "drama": 18,
    "familia": 10751,
    "fantasía": 14,
    "historia": 36,
    "terror": 27,
    "música": 10402,
    "misterio": 9648,
    "romance": 10749,
    "ciencia ficción": 878,
    "película de tv": 10770,
    "suspenso": 53,
    "bélica": 10752,
    "western": 37
}
GENRE_ID_TO_NAME = {v: k for k, v in GENRES.items()}

def get_movies_by_genre(genre):
    try:
        genre_id = GENRES.get(genre.lower())
        if not genre_id:
            logging.warning(f"Género desconocido: {genre}")
            return []

        url = f"{BASE_URL}/discover/movie"
        params = {
            "api_key": API_KEY,
            "with_genres": genre_id,
            "sort_by": "popularity.desc",
            "language": "es-ES"
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            logging.warning(f"No se encontraron películas para el género {genre}")
            return []
        
        logging.info(f"Películas encontradas para género: {genre}")
        return format_results(response.json().get("results", []), genre)
    except Exception as e:
        logging.exception(f"Error al obtener películas por género: {genre}")
        return []

def get_movies_filtered(genre, filters):
    try:
        genre_id = GENRES.get(genre.lower())
        if not genre_id:
            logging.warning(f"Género desconocido: {genre}")
            return []
        
        url = f"{BASE_URL}/discover/movie"
        params = {
            "api_key": API_KEY,
            "language": "es-ES",
            "with_genres": genre_id,
            "sort_by": "popularity.desc"
        }
        if "year" in filters:
            params["primary_release_year"] = filters["year"]

        response = requests.get(url, params=params)
        if response.status_code != 200:
            logging.warning(f"No se encontraron películas para el género {genre} y filtros {filters}")
            return []

        movies = response.json().get("results", [])

        if "actor" in filters:
            actor = filters["actor"]
            actor_id = get_actor_id(actor)
            if not actor_id:
                logging.warning(f"No se encontró el actor: {filters['actor']}")
                return []
            
            movies = [m for m in movies if actor_id in get_movie_actor_ids(m["id"])]

        logging.info(f"{len(movies)} películas encontradas con filtros: {filters}")
        return format_results(movies, genre)
    except Exception:
        logging.exception(f"Error al filtrar películas con género {genre} y filtros {filters}")
        return []

def get_actor_id(name):
    try:
        url = f"{BASE_URL}/search/person"
        params = {"api_key": API_KEY, "query": name, "language": "es-ES"}
        res = requests.get(url, params=params)
        if res.status_code != 200:
            logging.warning(f"No se encontró el actor: {name}")
            return None
        
        results = res.json().get("results")
        return results[0]["id"] if results else None
    except Exception:
        logging.exception(f"Error al obtener el ID del actor: {name}")
        return None

def get_movie_actor_ids(movie_id):
    try:
        url = f"{BASE_URL}/movie/{movie_id}/credits"
        params = {"api_key": API_KEY}
        res = requests.get(url, params=params)
        if res.status_code != 200:
            logging.warning(f"No se encontró el ID de la filmer: {movie_id}")
            return []
        
        cast = res.json().get("cast", [])
        return [c["id"] for c in cast[:5]]
    except Exception:
        logging.exception(f"Error al obtener actores de la película ID: {movie_id}")
        return []

def format_results(results, genre):
    movies = []
    for r in results:
        try:
            movies.append({
                "title": r.get("title"),
                "year": r.get("release_date", "")[:4],
                "genre": genre,
                "overview": r.get("overview", "Sin sinopsis disponible."),
                "actors": get_top_actors(r.get("id"))
            })
        except Exception:
            logging.exception(f"Error al formatear película: {r.get('title')}")
    return movies

def get_top_actors(movie_id):
    try:
        url = f"{BASE_URL}/movie/{movie_id}/credits"
        params = {"api_key": API_KEY}
        res = requests.get(url, params=params)
        if res.status_code != 200:
            logging.warning(f"No se encontró el ID de la película: {movie_id}")
            return []
        
        cast = res.json().get("cast", [])
        return [c["name"] for c in cast[:3]]
    except Exception:
        logging.exception(f"Error al obtener los actores principales del ID: {movie_id}")
        return []

def get_movies_by_franchise(franchise_name):
    try:
        url = f"{BASE_URL}/search/collection"
        params = {
            "api_key": API_KEY,
            "query": franchise_name,
            "language": "es-ES"
        }
        res = requests.get(url, params=params)
        if res.status_code != 200:
            logging.warning(f"No se encontró la franquicia: {franchise_name}")
            return []

        collections = res.json().get("results", [])
        if not collections:
            logging.warning(f"No se encontró la colección: {franchise_name}")
            return []

        collection_id = collections[0]['id']
        url = f"{BASE_URL}/collection/{collection_id}"
        res = requests.get(url, params={"api_key": API_KEY, "language": "es-ES"})
        if res.status_code != 200:
            logging.warning(f"No se encontró la colección id: {franchise_name}")
            return []

        parts = res.json().get("parts", [])
        logging.info(f"Franquicia '{franchise_name}' encontrada con {len(parts)} películas.")
        return format_results(parts, genre="franquicia")
    except Exception:
        logging.exception(f"Error al obtener películas de la franquicia: {franchise_name}")
        return []

def get_movie_by_title(title):
    try:
        url = f"{BASE_URL}/search/movie"
        params = {
            "api_key": API_KEY,
            "query": title,
            "language": "es-ES"
        }
        res = requests.get(url, params=params)
        if res.status_code != 200:
            logging.warning(f"No se encontró la filmer: {title}")
            return None

        results = res.json().get("results", [])
        if not results:
            logging.warning(f"No se encontró la película: {title}")
            return None

        movie = results[0]
        actors = get_top_actors(movie["id"])
        
        genre_ids = movie.get("genre_ids", [])
        genre_name = GENRE_ID_TO_NAME.get(genre_ids[0], "desconocido") if genre_ids else "desconocido"

        return {
            "title": movie.get("title"),
            "year": movie.get("release_date", "")[:4],
            "genre": genre_name,
            "overview": movie.get("overview", "Sin sinopsis disponible."),
            "actors": actors
        }
    except Exception:
        logging.exception(f"Error al buscar película por título: {title}")
        return None