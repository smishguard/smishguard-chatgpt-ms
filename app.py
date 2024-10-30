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
                        "otros servicios, y luego ajusta tu comentario final teniendo en cuenta el puntaje ponderado del riesgo para evitar generar confusión en el usuario.\n\n"
                        "### Proceso de evaluación:\n"
                        "1. **Análisis inicial**: Evalúa el mensaje basándote en patrones de phishing y asigna un valor entre 0 y 1, donde 0 indica que el mensaje parece seguro y 1 "
                        "indica un riesgo elevado. Considera:\n"
                        "   - Origen o legitimidad potencial del mensaje (por ejemplo, mensajes de bancos o servicios importantes), sin asumir que el remitente es seguro.\n"
                        "   - Características de phishing, como enlaces acortados o sospechosos, tono de urgencia inusual, o errores gramaticales.\n"
                        "   - URLs incluidas en el mensaje y cualquier patrón asociado con phishing.\n\n"
                        "2. **Comentario final considerando el puntaje ponderado**:\n"
                        "   Una vez que has dado tu valor de riesgo, ajusta tu comentario final teniendo en cuenta el puntaje ponderado de los tres servicios para evitar confusión:\n"
                        "   - Si el puntaje ponderado final indica que el mensaje es 'Seguro' (1 a 3), modera tu comentario para que no alarme innecesariamente. Enfócate en que "
                        "     el mensaje parece seguro, pero sugiere una revisión mínima en caso de duda.\n"
                        "   - Si el puntaje ponderado final indica 'Sospechoso' (4 a 7), señala que el mensaje tiene algunas características de riesgo y sugiere precaución.\n"
                        "   - Si el puntaje ponderado final indica 'Peligroso' (8 a 10), enfatiza los riesgos y advierte al usuario que probablemente sea un intento de phishing.\n\n"
                        "Responde en este formato JSON:\n"
                        "{\n"
                        "\"Calificación\": [valor entre 0 y 1 basado en tu análisis inicial del mensaje],\n"
                        "\"Comentario\": \"[Comentario final, ajustado al puntaje ponderado, para dar una evaluación consolidada que sea clara y coherente con el puntaje final]\"\n"
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
