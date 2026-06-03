"""
web_server.py - Servidor Backend Flask para CuscoNodes
Expone endpoints REST para orquestar los agentes de IA
"""

import json
import os
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from src.multi_agent_orchestrator import SupervisorAgent
from src.config.settings import Settings
from google import genai

app = Flask(__name__)
CORS(app)

HISTORY_FILE = os.path.join("data", "processed", "history.json")
RECIPIENTS_FILE = os.path.join("data", "recipients.json")


def _load_recipients():
    if os.path.exists(RECIPIENTS_FILE):
        with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"whatsapp": "", "email": ""}


def _save_recipients(data):
    with open(RECIPIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route('/')
def serve_dashboard():
    return send_from_directory(os.path.join(os.path.dirname(__file__), "web"), "index.html")


def _load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_history(entry):
    history = _load_history()
    history.insert(0, entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


@app.route('/api/orchestrate', methods=['POST'])
def orchestrate_agents():
    start = time.time()
    try:
        supervisor = SupervisorAgent()
        result_payload = supervisor.execute_pipeline()
        elapsed = round(time.time() - start, 2)

        history_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "urgencia": result_payload.get("urgencia", result_payload.get("clasificacion", "N/A")),
            "texto_crudo": result_payload.get("texto_crudo", result_payload.get("resumen_ia", ""))[:120],
            "traducciones": list(result_payload.get("traducciones", {}).keys()),
            "despacho": result_payload.get("despacho_status", {}).get("estado_final", "N/A"),
            "latencia_s": elapsed
        }
        _save_history(history_entry)

        result_payload["_latencia"] = elapsed
        return jsonify(result_payload), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(_load_history()[:20]), 200


@app.route('/api/query', methods=['POST'])
def query_ai():
    data = request.get_json(force=True)
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Por favor escribe una pregunta."}), 400

    try:
        client = genai.Client(api_key=Settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=(
                "Eres un asistente experto en turismo para Cusco, Perú. "
                "Responde preguntas sobre alertas, rutas, y recomendaciones para turistas. "
                "Preserva los topónimos sagrados sin traducir: Machu Picchu, Ollantaytambo, Sacsayhuamán, Pisac, Chinchero, Urubamba.\n\n"
                f"Pregunta: {question}"
            )
        )
        return jsonify({"answer": response.text.strip()}), 200
    except Exception as e:
        return jsonify({
            "answer": (
                "CuscoNodes está en modo de recursos limitados. "
                "Las consultas a la IA estarán disponibles cuando la cuota de Gemini se restablezca. "
                "Mientras tanto, puedes consultar alertas activas vía el orquestador."
            )
        }), 200


@app.route('/api/recipients', methods=['GET', 'POST'])
def manage_recipients():
    if request.method == 'GET':
        return jsonify(_load_recipients()), 200

    data = request.get_json(force=True)
    current = _load_recipients()
    if "whatsapp" in data:
        current["whatsapp"] = data["whatsapp"].strip()
    if "email" in data:
        current["email"] = data["email"].strip()
    _save_recipients(current)
    return jsonify({"status": "ok", "recipients": current}), 200


if __name__ == '__main__':
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    print("🚀 Servidor de CuscoNodes escuchando en http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
