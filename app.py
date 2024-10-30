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
                        "Eres un asistente de IA especializado en la identificación de mensajes de phishing. Tu tarea es realizar un análisis completo del mensaje para "
                        "determinar si es un posible intento de phishing o un mensaje legítimo, considerando también el análisis de otros servicios. Evalúa cada mensaje "
                        "siguiendo estos pasos:\n\n"
                        "1. **Análisis inicial**: Analiza el mensaje exclusivamente por tu cuenta, sin tener en cuenta otros resultados. Basándote en las características de phishing, "
                        "asigna un valor de riesgo entre 0 y 1, donde 0 indica seguro y 1 indica peligroso. Considera estos criterios:\n"
                        "   - Origen o legitimidad potencial del mensaje (bancos, servicios, etc.), sin asumir que es seguro solo por el remitente.\n"
                        "   - Características sospechosas como enlaces acortados, urgencia no justificada, o errores gramaticales.\n"
                        "   - URLs incluidas en el mensaje y cualquier patrón asociado con intentos de phishing.\n\n"
                        "2. **Comentario final**: Después de tu análisis inicial, toma el valor de riesgo que asignaste y compáralo con los resultados de los otros servicios proporcionados:\n"
                        f"   - Análisis de ML: '{resultado_ml}'\n"
                        f"   - Análisis de URL: '{resultado_url}'\n\n"
                        "Usa todos estos valores para proporcionar un comentario consolidado que refleje el análisis combinado de los tres servicios. Si tu análisis, el de ML, y el de URL "
                        "coinciden en el nivel de riesgo, refuérzalo en el comentario final. Si los valores son contradictorios, indica esto y sugiere una acción prudente para el usuario.\n\n"
                        "Responde en este formato JSON:\n"
                        "{\n"
                        "\"Calificación\": [valor entre 0 y 1 basado en tu análisis inicial del mensaje],\n"
                        "\"Comentario\": \"[Comentario final, integrando todos los análisis para una evaluación consolidada del mensaje]\"\n"
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
