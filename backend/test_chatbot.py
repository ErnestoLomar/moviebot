import pytest
from chatbot import Chatbot

@pytest.fixture
def bot():
    return Chatbot()

def test_tema_invalido(bot):
    response = bot.handle_message("¿Cómo arreglo mi celular?", session_id="test1")
    assert not response["movies"]
    assert "solo puedo hablar de películas" in response["reply"].lower()

def test_recomendacion_general(bot):
    response = bot.handle_message("Me gustan las películas de acción", session_id="test2")
    assert response["movies"]
    assert len(response["movies"]) <= 5
    assert "reply" in response

def test_filtrado_por_actor(bot):
    msg = "Recomiéndame películas de acción con Tom Cruise"
    response = bot.handle_message(msg, session_id="test3")
    assert response["movies"]
    assert any("Tom Cruise" in ", ".join(m["actors"]) for m in response["movies"])

def test_filtrado_por_anio(bot):
    msg = "¿Qué películas de terror hay del año 2020?"
    response = bot.handle_message(msg, session_id="test4")
    assert response["movies"]
    assert all("2020" in m["year"] for m in response["movies"] if m["year"])

def test_no_resultados(bot):
    msg = "Películas de comedia de 1850"
    response = bot.handle_message(msg, session_id="test5")
    assert not response["movies"]
    assert "no pude encontrar" in response["reply"].lower()