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
                        "determinar si es un posible intento de phishing o un mensaje legítimo, considerando también el análisis de otros servicios y el cálculo ponderado "
                        "de riesgo.\n\n"
                        "### Proceso de evaluación:\n"
                        "1. **Análisis inicial**: Realiza tu propio análisis del mensaje basándote en patrones de phishing, y asigna un valor de riesgo entre 0 y 1, donde 0 indica "
                        "que el mensaje parece seguro y 1 indica un riesgo elevado. Evalúa los siguientes criterios:\n"
                        "   - Origen o legitimidad del mensaje (por ejemplo, mensajes de bancos o servicios importantes), sin asumir automáticamente que es seguro.\n"
                        "   - Características de phishing, como enlaces acortados o sospechosos, tono de urgencia inusual, o errores gramaticales.\n"
                        "   - URLs incluidas en el mensaje y cualquier patrón que sugiera phishing.\n\n"
                        "2. **Comparación y ponderación**:\n"
                        "   Después de tu análisis inicial, considera los resultados proporcionados por otros servicios y ajusta tu comentario final de acuerdo al "
                        "cálculo ponderado. Estos son los resultados adicionales:\n"
                        f"   - Análisis de ML: '{resultado_ml}'\n"
                        f"   - Análisis de URL: '{resultado_url}'\n\n"
                        "   Dependiendo de los servicios disponibles, el puntaje ponderado final se calcula de la siguiente manera:\n"
                        "   - Si solo se tiene tu análisis y el de ML, entonces el análisis de ML tiene una ponderación del 60%, y el tuyo cuenta con un 40%.\n"
                        "   - Si tu análisis falta, entonces el puntaje depende en un 70% de ML y en un 30% del análisis de URL.\n"
                        "   - Si falta el análisis de ML, tu ponderación aumenta a un 70% y el análisis de URL pesa un 30%.\n"
                        "   - Si todos los servicios están disponibles, el análisis de ML tiene una ponderación de 40%, el análisis de URL 35%, y tu evaluación 25%.\n\n"
                        "3. **Comentario Final**:\n"
                        "   Según el cálculo ponderado, clasifica el mensaje como:\n"
                        "   - **Seguro** si el puntaje ponderado está entre 1 y 3,\n"
                        "   - **Sospechoso** si el puntaje está entre 4 y 7,\n"
                        "   - **Peligroso** si el puntaje está entre 8 y 10.\n\n"
                        "   Ajusta tu comentario para que sea consistente con el puntaje ponderado. Si el puntaje indica 'Seguro', usa un tono tranquilizador y evita generar "
                        "alarma. Si el puntaje indica 'Sospechoso' o 'Peligroso', advierte al usuario sobre los riesgos potenciales. Si tu análisis propio es diferente al puntaje final, "
                        "aclara que este resultado refleja un análisis combinado.\n\n"
                        "Responde en el siguiente formato JSON:\n"
                        "{\n"
                        "\"Calificación\": [valor entre 0 y 1 basado en tu análisis inicial del mensaje],\n"
                        "\"Comentario\": \"[Comentario final, ajustado al puntaje ponderado, proporcionando una evaluación consolidada y clara para el usuario]\"\n"
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
