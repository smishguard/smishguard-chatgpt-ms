import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    # Prueba de integración para el endpoint "/"
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Hello, world!'

def test_ping(client):
    # Prueba de integración para el endpoint "/ping"
    response = client.get('/ping')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {"message": "pong"}

@patch('app.client.chat.completions.create')
def test_consultar_modelo_integration(mock_openai_create, client):
    # Configurar el mock para la respuesta de OpenAI
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps({
        "Calificación": 0.5,
        "Descripción": "El mensaje parece legítimo pero tiene características sospechosas."
    })))]
    mock_openai_create.return_value = mock_response

    # Prueba de integración para el endpoint "/consultar-modelo-gpt" con datos válidos
    response = client.post('/consultar-modelo-gpt', json={"mensaje": "¿Es seguro este mensaje que me envió mi banco?"})
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "Calificación" in data
    assert "Descripción" in data

def test_consultar_modelo_mensaje_faltante_integration(client):
    # Prueba de integración para el endpoint "/consultar-modelo-gpt" sin el campo 'mensaje'
    response = client.post('/consultar-modelo-gpt', json={})
    assert response.status_code == 400

    data = json.loads(response.data)
    assert data == {"error": "El campo 'mensaje' es obligatorio."}

@patch('app.client.chat.completions.create')
def test_consultar_modelo_error_integration(mock_openai_create, client):
    # Configurar el mock para que lance una excepción
    mock_openai_create.side_effect = Exception("Error de prueba de OpenAI")

    # Prueba de integración para el endpoint "/consultar-modelo-gpt" manejando errores
    response = client.post('/consultar-modelo-gpt', json={"mensaje": "Prueba de error"})
    assert response.status_code == 500

    data = json.loads(response.data)
    assert data["error"] == "Ocurrió un error al procesar la solicitud."
    assert "detalles" in data

@patch('app.client.chat.completions.create')
def test_conclusion_modelo_integration(mock_openai_create, client):
    # Configurar el mock para la respuesta de OpenAI
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps({
        "conclusion": "Este mensaje es sospechoso debido a la urgencia y el uso de un enlace sospechoso."
    })))]
    mock_openai_create.return_value = mock_response

    # Prueba de integración para el endpoint "/conclusion-modelo-gpt" con datos válidos
    response = client.post('/conclusion-modelo-gpt', json={"resultado_parcial": "Resultado parcial de ejemplo"})
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "conclusion" in data
    assert data["conclusion"] == "Este mensaje es sospechoso debido a la urgencia y el uso de un enlace sospechoso."

def test_conclusion_modelo_resultado_parcial_faltante_integration(client):
    # Prueba de integración para el endpoint "/conclusion-modelo-gpt" sin el campo 'resultado_parcial'
    response = client.post('/conclusion-modelo-gpt', json={})
    assert response.status_code == 400

    data = json.loads(response.data)
    assert data == {"error": "El campo 'resultado_parcial' es obligatorio."}

@patch('app.client.chat.completions.create')
def test_conclusion_modelo_error_integration(mock_openai_create, client):
    # Configurar el mock para que lance una excepción
    mock_openai_create.side_effect = Exception("Error de prueba de OpenAI")

    # Prueba de integración para el endpoint "/conclusion-modelo-gpt" manejando errores
    response = client.post('/conclusion-modelo-gpt', json={"resultado_parcial": "Prueba de error en conclusión"})
    assert response.status_code == 500

    data = json.loads(response.data)
    assert data["error"] == "Ocurrió un error al procesar la solicitud."
    assert "detalles" in data
