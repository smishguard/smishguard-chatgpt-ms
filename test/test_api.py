import pytest
import json
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    # Prueba para el endpoint "/"
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Hello, world!'

def test_ping(client):
    # Prueba para el endpoint "/ping"
    response = client.get('/ping')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {"message": "pong"}

def test_consultar_modelo_valido(client, mocker):
    # Configuración del mock para simular la respuesta de OpenAI
    mock_response = {
        "Calificación": 0.5,
        "Descripción": "El mensaje parece legítimo pero tiene características sospechosas."
    }
    mock_create = mocker.patch('app.client.chat.completions.create')
    mock_create.return_value.choices = [type('obj', (object,), {"message": type('obj', (object,), {"content": json.dumps(mock_response)})})]

    # Solicitud POST válida al endpoint "/consultar-modelo-gpt"
    response = client.post('/consultar-modelo-gpt', json={"mensaje": "¿Es seguro este mensaje que me envió mi banco?"})
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["Calificación"] == 0.5
    assert "Descripción" in data

def test_consultar_modelo_mensaje_faltante(client):
    # Prueba para el endpoint "/consultar-modelo-gpt" sin el campo 'mensaje'
    response = client.post('/consultar-modelo-gpt', json={})
    assert response.status_code == 400

    data = json.loads(response.data)
    assert data == {"error": "El campo 'mensaje' es obligatorio."}

def test_consultar_modelo_error(client, mocker):
    # Configuración del mock para simular un error en OpenAI
    mock_create = mocker.patch('app.client.chat.completions.create')
    mock_create.side_effect = Exception("Error de prueba de OpenAI")

    # Prueba de solicitud POST al endpoint "/consultar-modelo-gpt" manejando errores
    response = client.post('/consultar-modelo-gpt', json={"mensaje": "Prueba de error"})
    assert response.status_code == 500

    data = json.loads(response.data)
    assert data["error"] == "Ocurrió un error al procesar la solicitud."
    assert "detalles" in data

def test_conclusion_modelo_valido(client, mocker):
    # Configuración del mock para simular la respuesta de OpenAI
    mock_response = {
        "conclusion": "Este mensaje es sospechoso debido a la urgencia y el uso de un enlace sospechoso."
    }
    mock_create = mocker.patch('app.client.chat.completions.create')
    mock_create.return_value.choices = [type('obj', (object,), {"message": type('obj', (object,), {"content": json.dumps(mock_response)})})]

    # Solicitud POST válida al endpoint "/conclusion-modelo-gpt"
    response = client.post('/conclusion-modelo-gpt', json={"resultado_parcial": "Resultado parcial de ejemplo"})
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "conclusion" in data
    assert data["conclusion"] == "Este mensaje es sospechoso debido a la urgencia y el uso de un enlace sospechoso."

def test_conclusion_modelo_resultado_parcial_faltante(client):
    # Prueba para el endpoint "/conclusion-modelo-gpt" sin el campo 'resultado_parcial'
    response = client.post('/conclusion-modelo-gpt', json={})
    assert response.status_code == 400

    data = json.loads(response.data)
    assert data == {"error": "El campo 'resultado_parcial' es obligatorio."}

def test_conclusion_modelo_error(client, mocker):
    # Configuración del mock para simular un error en OpenAI
    mock_create = mocker.patch('app.client.chat.completions.create')
    mock_create.side_effect = Exception("Error de prueba de OpenAI")

    # Prueba de solicitud POST al endpoint "/conclusion-modelo-gpt" manejando errores
    response = client.post('/conclusion-modelo-gpt', json={"resultado_parcial": "Prueba de error en conclusión"})
    assert response.status_code == 500

    data = json.loads(response.data)
    assert data["error"] == "Ocurrió un error al procesar la solicitud."
    assert "detalles" in data
