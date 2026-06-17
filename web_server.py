import csv
import io
import json
import logging
import os
import time
from collections import Counter
from datetime import datetime
from functools import wraps
from threading import Lock
from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from src.multi_agent_orchestrator import SupervisorAgent
from src.config.settings import Settings
from google import genai

app = Flask(__name__)
CORS(app)

HISTORY_FILE = os.path.join("data", "processed", "history.json")
RECIPIENTS_FILE = os.path.join("data", "recipients.json")
MONITORING_FILE = os.path.join("data", "monitoring.json")
LOG_FILE = os.path.join("data", "pipeline.log")

os.makedirs(os.path.join("data", "processed"), exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

scheduler = BackgroundScheduler()
scheduler_lock = Lock()
SCHEDULER_JOB_ID = "pipeline_job"


def _load_json(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _update_monitoring(status, message=None):
    mon = _load_json(MONITORING_FILE, {"total": 0, "success": 0, "failed": 0, "last_execution": None, "last_success": None, "last_error": None})
    mon["total"] += 1
    mon["last_execution"] = datetime.now().isoformat()
    if status == "success":
        mon["success"] += 1
        mon["last_success"] = datetime.now().isoformat()
    else:
        mon["failed"] += 1
        mon["last_error"] = {"time": datetime.now().isoformat(), "message": message or "Unknown error"}
    _save_json(MONITORING_FILE, mon)


def _run_pipeline_job():
    logging.info("Scheduler: iniciando pipeline")
    try:
        s = SupervisorAgent()
        r = s.execute_pipeline()
        d = r.get("despacho_status", {}).get("estado_final", "N/A")
        _update_monitoring("success")
        logging.info(f"Scheduler: pipeline completado - estado: {d}")
    except Exception as e:
        _update_monitoring("failed", str(e))
        logging.error(f"Scheduler: pipeline falló - {e}")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def serve_dashboard():
    return send_from_directory(os.path.join(os.path.dirname(__file__), "web"), "index.html")


@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()}), 200


@app.route('/api/ping')
def ping():
    print("[PING] server alive")
    return "pong", 200


@app.route('/api/login', methods=['POST'])
def login():
    return jsonify({"status": "ok"}), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    return jsonify({"status": "ok"}), 200


@app.route('/api/auth/status')
def auth_status():
    return jsonify({"authenticated": True}), 200


@app.route('/api/orchestrate', methods=['POST'])
@login_required
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
        history = _load_json(HISTORY_FILE, [])
        history.insert(0, history_entry)
        _save_json(HISTORY_FILE, history)
        _update_monitoring("success")
        result_payload["_latencia"] = elapsed
        return jsonify(result_payload), 200
    except Exception as e:
        _update_monitoring("failed", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/history')
@login_required
def get_history():
    return jsonify(_load_json(HISTORY_FILE, [])[:50]), 200


@app.route('/api/metrics')
@login_required
def get_metrics():
    history = _load_json(HISTORY_FILE, [])
    total = len(history)
    if not total:
        return jsonify({"total_ejecuciones": 0, "alertas_por_dia": {}, "latencia_promedio_s": 0, "tasa_exito": 0, "distribucion_urgencia": {}, "ultima_ejecucion": None}), 200
    dates = Counter()
    latencies = []
    despachados = 0
    urgencias = Counter()
    for h in history:
        ts = h.get("timestamp", "")
        if ts:
            dates[ts[:10]] += 1
        lat = h.get("latencia_s", 0)
        if isinstance(lat, (int, float)):
            latencies.append(lat)
        if h.get("despacho") == "despachado":
            despachados += 1
        urg = h.get("urgencia", "N/A")
        if urg:
            urgencias[urg] += 1
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    return jsonify({
        "total_ejecuciones": total,
        "alertas_por_dia": dict(sorted(dates.items())),
        "latencia_promedio_s": round(avg_latency, 2),
        "tasa_exito": round(despachados / total * 100, 1) if total else 0,
        "distribucion_urgencia": dict(urgencias),
        "ultima_ejecucion": history[0].get("timestamp") if history else None
    }), 200


@app.route('/api/export/csv')
@login_required
def export_csv():
    history = _load_json(HISTORY_FILE, [])
    if not history:
        return Response("Sin datos", mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=historial.csv"})
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(history[0].keys())
    for entry in history:
        writer.writerow(entry.values())
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=historial_cusconodes.csv"})


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
@login_required
def manage_recipients():
    if request.method == 'GET':
        return jsonify(_load_json(RECIPIENTS_FILE, {"whatsapp": "", "email": ""})), 200
    data = request.get_json(force=True)
    current = _load_json(RECIPIENTS_FILE, {"whatsapp": "", "email": ""})
    if "whatsapp" in data:
        current["whatsapp"] = data["whatsapp"].strip()
    if "email" in data:
        current["email"] = data["email"].strip()
    _save_json(RECIPIENTS_FILE, current)
    return jsonify({"status": "ok", "recipients": current}), 200


@app.route('/api/scheduler/start', methods=['POST'])
@login_required
def start_scheduler():
    with scheduler_lock:
        if scheduler.get_job(SCHEDULER_JOB_ID):
            return jsonify({"status": "already_running"}), 200
        interval = request.get_json(force=True).get("interval", 30)
        scheduler.add_job(_run_pipeline_job, "interval", minutes=int(interval), id=SCHEDULER_JOB_ID, replace_existing=True)
        scheduler.start()
        logging.info(f"Scheduler iniciado cada {interval} min")
        return jsonify({"status": "started", "interval_min": interval}), 200


@app.route('/api/scheduler/stop', methods=['POST'])
@login_required
def stop_scheduler():
    with scheduler_lock:
        if scheduler.get_job(SCHEDULER_JOB_ID):
            scheduler.remove_job(SCHEDULER_JOB_ID)
        if scheduler.running:
            scheduler.shutdown(wait=False)
    logging.info("Scheduler detenido")
    return jsonify({"status": "stopped"}), 200


@app.route('/api/scheduler/status')
@login_required
def scheduler_status():
    job = scheduler.get_job(SCHEDULER_JOB_ID)
    return jsonify({
        "running": job is not None,
        "interval_min": int(job.trigger.interval.seconds / 60) if job else None,
        "next_run": job.next_run_time.isoformat() if job and job.next_run_time else None
    }), 200


@app.route('/api/monitoring')
@login_required
def get_monitoring():
    mon = _load_json(MONITORING_FILE, {"total": 0, "success": 0, "failed": 0, "last_execution": None, "last_success": None, "last_error": None})
    scheduler_info = scheduler_status()
    mon["scheduler"] = scheduler_info[0].json if hasattr(scheduler_info[0], 'json') else scheduler_info
    return jsonify(mon), 200


if __name__ == '__main__':
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor CuscoNodes en http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
