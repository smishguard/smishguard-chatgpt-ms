from flask import Flask, jsonify, request
from openai import OpenAI
from datetime import datetime
from model.MensajeSMS import MensajeSMS
from model.Alerta import Alerta
from model.Analisis import Analisis
import json
import requests  # Importa la biblioteca requests para realizar solicitudes HTTP

app = Flask(__name__)
application = app
client = OpenAI()

@app.route('/')
def hello_world():
    return 'hello, world!'

@app.route("/ping")
def ping():
    return jsonify({"message": "pong"})

@app.route("/consultar-modelo-gpt", methods=['POST'])
def consultar_modelo():
    # Obtener el objeto JSON enviado en el cuerpo de la solicitud
    data = request.get_json()
    mensaje = data.get('mensaje', '')

    # Realizar la solicitud a la API de OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "Eres un asistente de IA especializado en identificar mensajes de phishing. Proporciona una probabilidad entre 0 (no peligroso) y 1 (muy peligroso). Responde en el siguiente formato JSON: { \"Calificación\": [número], \"Descripción\": \"[breve explicación]\" }"},
            {"role": "user", "content": f'Evalúa este mensaje: "{mensaje}"'}
        ]
    )

    # Convertir la cadena JSON a un objeto Python
    response_json_openai = json.loads(response.choices[0].message.content)

    # Retornar el objeto JSON combinado en la respuesta
    return jsonify(response_json_openai)

if __name__ == '__main__':
    app.run(debug = True)
