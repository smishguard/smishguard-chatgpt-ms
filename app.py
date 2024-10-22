from flask import Flask, jsonify, request
from openai import OpenAI
import json

app = Flask(__name__)
application = app
client = OpenAI()

@app.route('/')
def hello_world():
    return 'Hello, world!'

@app.route("/ping")
def ping():
    return jsonify({"message": "pong"})

@app.route("/consultar-modelo-gpt", methods=['POST'])
def consultar_modelo():
    # Obtener el objeto JSON enviado en el cuerpo de la solicitud
    data = request.get_json()
    mensaje = data.get('mensaje', '')

    if not mensaje:
        return jsonify({"error": "El campo 'mensaje' es obligatorio."}), 400

    try:
        # Realizar la solicitud a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente de IA especializado en identificar mensajes de phishing, pero también "
                        "puedes reconocer mensajes legítimos de entidades bancarias y de salud. Evalúa el mensaje considerando "
                        "lo siguiente: algunos mensajes pueden ser de instituciones legítimas, como bancos notificando transacciones "
                        "o entidades de salud compartiendo campañas de prevención. Considera si el mensaje parece auténtico o si "
                        "contiene características comunes de phishing (como enlaces sospechosos, urgencia inusual o solicitudes de "
                        "información personal). Si hay URLs, evalúa su seguridad y proporciona recomendaciones sobre ellas. "
                        "Proporciona una probabilidad entre 0 (no peligroso) y 1 (muy peligroso). "
                        "No todo lo que tenga que ver con algún banco es seguro, si habla sobre créditos o productos aprobados puede ser una trampa, tenlo en cuenta. "
                        "Responde en el siguiente formato JSON: "
                        "{ "
                        "\"Calificación\": [número], "
                        "\"Descripción\": \"[breve explicación que incluya la evaluación y cualquier recomendación o advertencia]\" "
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": f'Evalúa este mensaje: "{mensaje}"'
                }
            ]
        )

        # Acceder al contenido de la respuesta de forma correcta
        response_content = response.choices[0].message.content
        response_json_openai = json.loads(response_content)

        # Retornar el objeto JSON en la respuesta
        return jsonify(response_json_openai)

    except Exception as e:
        # Manejo de errores en caso de que ocurra una excepción y registro del error
        app.logger.error(f"Error al consultar el modelo de OpenAI: {e}")
        return jsonify({"error": "Ocurrió un error al procesar la solicitud.", "detalles": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
