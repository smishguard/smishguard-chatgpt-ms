# Análisis de Mensajes con Modelo GPT - API en Flask

## Descripción

Esta API ofrece un servicio para analizar mensajes y evaluar su potencial de phishing o autenticidad utilizando el modelo de lenguaje de OpenAI, `gpt-3.5-turbo-0125`. La API está diseñada para ayudar a identificar amenazas de phishing o verificar la legitimidad de mensajes de texto. Este servicio ya está desplegado en **Render**.

## Endpoints

### 1. `GET /`

#### Descripción
Endpoint básico para probar que el servicio esté funcionando.

#### Respuesta
```json
"Hello, world!"
```

### 2. `GET /ping`

#### Descripción
Endpoint de prueba para verificar la disponibilidad de la API.

#### Respuesta
```json
{
    "message": "pong"
}
```

### 3. `POST /consultar-modelo-gpt`

#### Descripción
Este endpoint permite analizar un mensaje con el modelo GPT para identificar si es potencialmente peligroso (phishing) o legítimo. El modelo utiliza criterios específicos de identificación de phishing.

#### Solicitud
- **URL**: `/consultar-modelo-gpt`
- **Método**: `POST`
- **Body**: JSON con el campo `mensaje`.

```json
{
    "mensaje": "Texto del mensaje a analizar"
}
```

#### Respuesta
El modelo responde con un JSON que contiene una calificación de riesgo entre 0 y 1, donde 0 indica baja peligrosidad y 1 alto riesgo de phishing.

```json
{
    "Calificación": 0.5
}
```

#### Errores
Si el campo `mensaje` está vacío o no se incluye:

```json
{
    "error": "El campo 'mensaje' es obligatorio."
}
```

Si ocurre un error interno al procesar la solicitud:

```json
{
    "error": "Ocurrió un error al procesar la solicitud.",
    "detalles": "Detalles del error"
}
```

### 4. `POST /conclusion-modelo-gpt`

#### Descripción
Este endpoint genera una conclusión basada en el análisis de diferentes parámetros de riesgo del mensaje. Recibe una evaluación previa y utiliza el modelo GPT para clasificar el nivel de riesgo y recomendar acciones de seguridad.

#### Solicitud
- **URL**: `/conclusion-modelo-gpt`
- **Método**: `POST`
- **Body**: JSON con el campo `resultado_parcial`, que contiene datos previos del análisis.

```json
{
    "resultado_parcial": {
        "valor_gpt": "Información adicional de GPT",
        "analisis_smishguard": "Sospechoso",
        "enlace": "http://example.com",
        "resultado_url": "Seguro",
        "resultado_ml": "Extra data",
        "mensaje_analizado": "Texto del mensaje",
        "numero_celular": "+123456789",
        "puntaje": 7
    }
}
```

#### Respuesta
El modelo responde con una conclusión y recomendaciones específicas sobre el mensaje en formato JSON.

```json
{
    "conclusion": "El mensaje es sospechoso. Se recomienda evitar hacer clic en enlaces y verificar la autenticidad del remitente por otros medios."
}
```

#### Errores
Si el campo `resultado_parcial` está vacío o no se incluye:

```json
{
    "error": "El campo 'resultado_parcial' es obligatorio."
}
```

Si ocurre un error interno al procesar la solicitud:

```json
{
    "error": "Ocurrió un error al procesar la solicitud.",
    "detalles": "Detalles del error"
}
```

## Instalación y Ejecución Local

1. Clona el repositorio.

```bash
git clone <URL_del_repositorio>
cd <nombre_del_directorio>
```

2. Instala las dependencias necesarias.

```bash
pip install -r requirements.txt
```

3. Configura tus credenciales de OpenAI en el archivo de variables de entorno o directamente en el código.

4. Ejecuta la aplicación.

```bash
python app.py
```

La API estará disponible en `http://127.0.0.1:5000`.

## Despliegue en Render

Este servicio está desplegado en Render. Al realizar una solicitud a cualquiera de los endpoints documentados, asegúrate de usar la URL de despliegue proporcionada por Render.

La API está disponible en: `https://smishguard-chatgpt-ms.onrender.com`.

## Licencia

Este proyecto está licenciado bajo la MIT License.

