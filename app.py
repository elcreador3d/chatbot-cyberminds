# app.py

# Importamos las librerías necesarias
from flask import Flask, request, jsonify
from rasa.core.agent import Agent
from rasa.shared.utils.io import json_to_string
import asyncio
import os

# Creamos la aplicación Flask
app = Flask(__name__)

# --- CONFIGURACIÓN DEL MODELO DE RASA ---
# Asegúrate de que el nombre de archivo del modelo sea el correcto.
# El nombre debe coincidir exactamente con el archivo .tar.gz en tu carpeta 'models'.
model_path = os.path.join(os.getcwd(), 'models', '20250804-095308-average-curve.tar.gz')

# Creamos un agente de Rasa. Esto cargará nuestro modelo entrenado.
# Manejamos los errores en caso de que el modelo no se pueda cargar.
try:
    agent = Agent.load(model_path)
    print("Modelo de Rasa cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar el modelo de Rasa en {model_path}: {e}")
    agent = None # Si el modelo no se carga, el agente será nulo.

# --- RUTAS DE LA API ---

@app.route("/")
def hello():
    """
    Ruta de bienvenida para verificar que el servidor está activo.
    Responde con el estado del bot.
    """
    if agent:
        return jsonify({"status": "Servidor de Rasa activo y listo para recibir mensajes."})
    else:
        return jsonify({"status": "Error: Servidor de Rasa activo, pero el modelo no se pudo cargar."}), 500

@app.route('/webhooks/rest/webhook', methods=['POST'])
async def webhook():
    """
    Ruta que actúa como el webhook de Rasa.
    Recibe un mensaje de un usuario y envía una respuesta.
    """
    # Si el agente no está cargado, no podemos procesar el mensaje.
    if not agent:
        return jsonify({"error": "El modelo de Rasa no está disponible."}), 503

    # Obtenemos el cuerpo de la petición JSON
    user_message_data = request.json
    sender_id = user_message_data.get('sender', 'default')
    message = user_message_data.get('message', '')

    print(f"Mensaje recibido de {sender_id}: {message}")

    try:
        # Enviamos el mensaje al agente de Rasa para obtener las respuestas
        responses = await agent.handle_text(message, sender_id=sender_id)
        print(f"Respuestas de Rasa: {responses}")

        # Preparamos las respuestas en el formato correcto para el frontend
        formatted_responses = []
        for response in responses:
            formatted_responses.append({
                "recipient_id": sender_id,
                "text": response.get("text", "")
            })

        return jsonify(formatted_responses)

    except Exception as e:
        # Manejo de errores en caso de fallo al procesar el mensaje
        print(f"Error al procesar el mensaje: {e}")
        return jsonify({"error": str(e)}), 500

# --- INICIO DE LA APLICACIÓN ---

if __name__ == '__main__':
    # Esta parte se ejecuta solo si corres el archivo directamente
    # desde la terminal, por ejemplo: `python app.py`.
    # En Render, Gunicorn se encargará de esto.
    app.run(debug=True, host='0.0.0.0', port=os.environ.get("PORT", 5005))
