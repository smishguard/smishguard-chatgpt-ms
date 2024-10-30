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
    resultado_ml = data.get('resultado_ml', 'No disponible')
    resultado_url = data.get('resultado_url', 'Indeterminado')

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
                        "Eres un asistente de IA especializado en identificar mensajes de phishing y evaluar su riesgo. Primero, realiza un análisis propio del mensaje sin considerar "
                        "otros servicios, y luego ajusta tu comentario final teniendo en cuenta la ponderación del riesgo.\n\n"
                        "### Proceso de evaluación:\n"
                        "1. **Análisis inicial**: Evalúa el mensaje basándote en patrones de phishing y asigna un valor entre 0 y 1, donde 0 indica que el mensaje parece seguro y 1 "
                        "indica un riesgo elevado. Considera:\n"
                        "   - Origen o legitimidad potencial del mensaje (por ejemplo, mensajes de bancos o servicios importantes), sin asumir que el remitente es seguro.\n"
                        "   - Características de phishing, como enlaces acortados o sospechosos, tono de urgencia inusual, o errores gramaticales.\n"
                        "   - URLs incluidas en el mensaje y cualquier patrón asociado con phishing.\n\n"
                        "2. **Comentario final considerando el cálculo ponderado**:\n"
                        "   Una vez que has dado tu valor de riesgo, ajusta tu comentario final teniendo en cuenta estos factores y la ponderación que se aplica en el cálculo final:\n"
                        "   - Si **solo el análisis de ML y GPT** están disponibles, el análisis de ML pesa más (60%) y el tuyo cuenta con un 40%.\n"
                        "   - Si **faltas tú (GPT)**, entonces el análisis depende en un 70% de ML y en un 30% del análisis de URL.\n"
                        "   - Si **falta el análisis de ML**, tu ponderación aumenta a un 70% y el análisis de URL pesa un 30%.\n"
                        "   - Si **todos los servicios están disponibles**, entonces el análisis de ML tiene una ponderación de 40%, el análisis de URL 35%, y tu evaluación 25%.\n\n"
                        "   Según el peso ponderado de tu valor y el valor combinado de los otros análisis, proporciona un comentario claro que refuerce o modere el nivel de riesgo "
                        "dependiendo de estos factores. Esto asegurará que el usuario entienda si el riesgo es **Seguro** (puntaje final <= 3), **Sospechoso** (puntaje final <= 7), o **Peligroso** (puntaje final > 7).\n\n"
                        "Responde en este formato JSON:\n"
                        "{\n"
                        "\"Calificación\": [valor entre 0 y 1 basado en tu análisis inicial del mensaje],\n"
                        "\"Comentario\": \"[Comentario final, ajustado a la ponderación y dando una evaluación consolidada del mensaje que evite confusión para el usuario]\"\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": f'Evalúa este mensaje: "{mensaje}"'
                }
            ]


        )

        # Acceder al contenido de la respuesta de OpenAI y cargar el JSON
        response_content = response.choices[0].message.content
        response_json_openai = json.loads(response_content)

        # Obtener la calificación y comentario final de GPT
        calificacion_gpt = response_json_openai.get("Calificación", 0)
        comentario_final = response_json_openai.get("Comentario", "Sin comentario")

        # Retornar el objeto JSON en la respuesta
        return jsonify({
            "Calificación": calificacion_gpt,
            "Comentario": comentario_final
        })

    except Exception as e:
        # Manejo de errores en caso de que ocurra una excepción y registro del error
        app.logger.error(f"Error al consultar el modelo de OpenAI: {e}")
        return jsonify({"error": "Ocurrió un error al procesar la solicitud.", "detalles": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
