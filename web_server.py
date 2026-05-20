"""
web_server.py - Servidor Backend Flask para CuscoNodes
Expone endpoints REST para orquestar los agentes de IA
"""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
from src.multi_agent_orchestrator import SupervisorAgent

app = Flask(__name__)
CORS(app)


@app.route('/api/orchestrate', methods=['POST'])
def orchestrate_agents():
    try:
        supervisor = SupervisorAgent()
        result_payload = supervisor.execute_pipeline()
        return jsonify(result_payload), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    print("🚀 Servidor de CuscoNodes escuchando en http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
