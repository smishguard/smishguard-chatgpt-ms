import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, json
from app import app

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        # Configuración para el cliente de pruebas de Flask
        self.app = app.test_client()
        self.app.testing = True

    def test_hello_world(self):
        # Prueba para el endpoint "/"
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello, world!')

    def test_ping(self):
        # Prueba para el endpoint "/ping"
        response = self.app.get('/ping')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, {"message": "pong"})

    @patch('app.client.chat.completions.create')
    def test_consultar_modelo(self, mock_openai_create):
        # Configurar el mock para la respuesta de OpenAI
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps({
            "Calificación": 0.5,
            "Descripción": "El mensaje parece legítimo pero tiene características sospechosas."
        })))]
        mock_openai_create.return_value = mock_response

        # Prueba para el endpoint "/consultar-modelo-gpt" con datos válidos
        response = self.app.post('/consultar-modelo-gpt', json={"mensaje": "¿Es este un mensaje seguro?"})
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("Calificación", data)
        self.assertIn("Descripción", data)

    def test_consultar_modelo_mensaje_faltante(self):
        # Prueba para el endpoint "/consultar-modelo-gpt" sin el campo 'mensaje'
        response = self.app.post('/consultar-modelo-gpt', json={})
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertEqual(data, {"error": "El campo 'mensaje' es obligatorio."})

    @patch('app.client.chat.completions.create')
    def test_consultar_modelo_error(self, mock_openai_create):
        # Configurar el mock para que lance una excepción
        mock_openai_create.side_effect = Exception("Error de prueba de OpenAI")

        # Prueba para el endpoint "/consultar-modelo-gpt" manejando errores
        response = self.app.post('/consultar-modelo-gpt', json={"mensaje": "Prueba de error"})
        self.assertEqual(response.status_code, 500)

        data = json.loads(response.data)
        self.assertEqual(data["error"], "Ocurrió un error al procesar la solicitud.")
        self.assertIn("detalles", data)

if __name__ == '__main__':
    unittest.main()
