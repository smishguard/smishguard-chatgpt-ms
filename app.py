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
                        "Eres un asistente de IA especializado en la identificación de mensajes de phishing. Además, eres capaz de reconocer mensajes legítimos, "
                        "como aquellos provenientes de bancos, entidades de salud, operadores de telefonía móvil o proveedores de servicios. Evalúa cada mensaje "
                        "según estos criterios: \n\n"
                        "1. **Legitimidad potencial**: Algunos mensajes pueden ser de instituciones legítimas, como bancos que notifican transacciones, "
                        "entidades de salud en campañas de prevención o promociones de operadores de telefonía y productos. No asumas que un mensaje es seguro "
                        "por venir de un banco; mensajes sobre créditos o productos aprobados pueden ser intentos de phishing.\n\n"
                        "2. **Características de phishing**: Reconoce las características de phishing, como:\n"
                        "   - Enlaces sospechosos o acortados.\n"
                        "   - Solicitudes urgentes de información o urgencia inusual.\n"
                        "   - Errores gramaticales o de ortografía.\n\n"
                        "3. **URLs y seguridad**: Si el mensaje incluye URLs, evalúa su seguridad y proporciona recomendaciones. Considera si los enlaces "
                        "parecen confiables o si presentan patrones asociados con phishing.\n\n"
                        "Responde en el siguiente formato JSON para estandarizar la evaluación:\n"
                        "{\n"
                        "\"Calificación\": [valor entre 0 y 1, donde 0 indica que no es peligroso y 1 indica muy peligroso],\n"
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
        

@app.route("/conclusion-modelo-gpt", methods=['POST'])
def conclucion_modelo():
    # Obtener el objeto JSON enviado en el cuerpo de la solicitud
    data = request.get_json()
    resultado_final = data.get('resultado_final', '')

    if not resultado_final:
        return jsonify({"error": "El campo 'resultado_final' es obligatorio."}), 400

    try:
        # Realizar la solicitud a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Imagina que estás analizando un mensaje de texto desde una perspectiva de seguridad cibernética. Recibes el análisis en una estructura que contiene varios elementos con los siguientes valores específicos:"
                        "valor_gpt: Valor adicional de la IA que proporciona información general."
                        "analisis_smishguard: Clasificación básica de seguridad del mensaje analizado (puede ser Seguro, Sospechoso o Peligroso)."
                        "enlace: URL analizada para ver su nivel de seguridad."
                        "resultado_url: Resultado sobre la seguridad del enlace."
                        "resultado_ml: Información extra de un modelo de machine learning."
                        "mensaje_analizado: Contenido textual del mensaje recibido."
                        "numero_celular: Número del remitente o destinatario."
                        "puntaje: Escala numérica del 1 al 10 que representa el nivel de riesgo del mensaje (según la siguiente escala):"
                        "1-3: Seguro"
                        "4-7: Sospechoso"
                        "8-10: Peligroso"
                        "Con esta información, tu tarea es generar una conclusión sobre la seguridad del mensaje mensaje_analizado. Usa los valores de analisis_smishguard y puntaje para definir el nivel de riesgo del mensaje. La conclusión debe incluir recomendaciones específicas basadas en el riesgo del mensaje, utilizando la siguiente lógica:"
                        "Si el mensaje es Seguro (puntaje 1-3): Describe por qué se considera seguro y sugiere mantener buenas prácticas generales de seguridad, como verificar la identidad del remitente cuando sea necesario."
                        "Si el mensaje es Sospechoso (puntaje 4-7): Advierte al usuario sobre la naturaleza sospechosa del mensaje. Recomienda evitar hacer clic en enlaces desconocidos y sugiere verificar la autenticidad del remitente a través de otros medios, como llamada telefónica o correo oficial."
                        "Si el mensaje es Peligroso (puntaje 8-10): Avisa al usuario sobre el alto nivel de riesgo y aconseja eliminar el mensaje inmediatamente. También sugiere evitar toda interacción con el contenido o los enlaces que incluye y advierte sobre los peligros de posibles fraudes o robo de información."
                        "Responde en el siguiente formato JSON para estandarizar la evaluación:\n"
                        "{\n"
                        "\"conclusion\": \"[conclusión creada a partir de la lógica mencionada anteriormente]\"\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": f'Dale una conclusión a este mensaje: "{resultado_final}"'
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
