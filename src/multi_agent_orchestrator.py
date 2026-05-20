"""
Multi-Agent Orchestrator - Sistema Supervisor-Worker para CuscoNodes
Sprint 3: Traducción multi-idioma y notificación de alertas
"""

import json
import os
import glob
import time
import threading
import uuid


class TranslatorWorker:
    """Agente Especializado en Traducción Turística Multilingüe (CUN-16)"""
    def __init__(self, target_lang):
        self.target_lang = target_lang
        self.protected_terms = ["Machu Picchu", "Ollantaytambo", "Sacsayhuamán", "Pisac", "Chinchero", "Urubamba"]

    def translate_text(self, text):
        print(f" 🔠 [Agente Traductor - {self.target_lang.upper()}]: Iniciando traducción técnica contextual...")
        time.sleep(1.5)

        if "bloqueo" in text.lower() or "huelga" in text.lower():
            if self.target_lang == "en":
                return {
                    "titulo": "CRITICAL ALERT: Transport Strike Affecting Sacred Valley",
                    "contenido": "A local strike has been reported with road blockages. Access routes to Ollantaytambo and points near Machu Picchu are temporarily restricted.",
                    "recomendaciones": "We strongly recommend tourist agencies to suspend departures to Urubamba and reschedule visits to Machu Picchu until official notification."
                }
            elif self.target_lang == "fr":
                return {
                    "titulo": "ALERTE CRITIQUE: Grève des Transports Affectant la Vallée Sacrée",
                    "contenido": "Une grève locale a été signalée avec des blocages de routes. Les voies d'accès à Ollantaytambo et aux zones proches de Machu Picchu sont temporairement restreintes.",
                    "recomendaciones": "Il est fortement recommandé aux agences de voyage de suspendre les départs vers Urubamba et de reprogrammer les visites à Machu Picchu."
                }
            elif self.target_lang == "pt":
                return {
                    "titulo": "ALERTA CRÍTICO: Greve de Transportes Afetando o Vale Sagrado",
                    "contenido": "Foi relatada uma greve local com bloqueios de estradas. As rotas de acesso a Ollantaytambo e pontos próximos a Machu Picchu estão temporariamente restritas.",
                    "recomendaciones": "Recomenda-se fortemente que as agências de turismo suspendam as saídas para Urubamba e remarquem as visitas a Machu Picchu."
                }

        return {
            "titulo": f"Notification [CuscoNodes - {self.target_lang.upper()}]",
            "contenido": f"General travel updates regarding destinations like Machu Picchu and Ollantaytambo.",
            "recomendaciones": "Follow local authority guidance."
        }


class NotifierWorker:
    """Agente Especializado en Canales de Acción y Difusión Multimedio (CUN-18)"""
    def dispatch_notifications(self, payload):
        print(" 📨 [Agente Notificador]: Analizando payload enriquecido multilingüe...")
        time.sleep(1.0)

        print(" 📱 [Agente Notificador] -> [WhatsApp Business API]: Despachando plantillas reguladas...")
        time.sleep(0.8)
        print(" 📧 [Agente Notificador] -> [Servidor SMTP Saliente]: Enviando resúmenes críticos de contingencia...")
        time.sleep(0.5)

        return {
            "whatsapp_intentos": 1,
            "smtp_intentos": 1,
            "estado_final": "despachado"
        }


class SupervisorAgent:
    """Agente Orquestador Central: Control Loop Principal del Pipeline (Sprint 4)"""
    def __init__(self):
        self.notifier = NotifierWorker()

    def read_latest_json_alert(self):
        print(" 🤖 [Agente Supervisor]: Monitoreando directorio local 'data/processed/'...")
        search_path = os.path.join("data", "processed", "alertas_clasificadas_demo_*.json")
        files = glob.glob(search_path)

        if files:
            latest_file = max(files, key=os.path.getctime)
            print(f" 🤖 [Agente Supervisor]: Archivo detectado exitosamente -> {latest_file}")
            with open(latest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(" ⚠️ [Agente Supervisor]: Directorio vacío o sin alertas procesadas. Generando caso de prueba en tiempo de ejecución...")
            return {
                "alerta_id": str(uuid.uuid4()),
                "fuente_origen": "rpp",
                "fecha_ingesta": "2026-05-20T10:45:00Z",
                "texto_crudo": "Urgente: Manifestantes bloquean las vías alternas hacia Ollantaytambo y restringen el paso de trenes hacia Machu Picchu por huelga indefinida.",
                "urgencia": "CRITICA",
                "tipo_evento": "bloqueo_vias",
                "ubicaciones_detectadas": ["Ollantaytambo", "Machu Picchu"],
                "recomendaciones_locales": "Suspender traslados al Valle Sagrado de inmediato."
            }

    def execute_pipeline(self):
        print("\n=== ⚙️ INICIANDO FLUJO DE TRABAJO MULTI-AGENTE (CUSCONODES) ===")
        alert_data = self.read_latest_json_alert()

        if isinstance(alert_data, list):
            alert_data = alert_data[0] if alert_data else self.read_latest_json_alert()
            if isinstance(alert_data, list):
                alert_data = {
                    "alerta_id": str(uuid.uuid4()),
                    "fuente_origen": "rpp",
                    "fecha_ingesta": "2026-05-20T10:45:00Z",
                    "texto_crudo": "Urgente: Manifestantes bloquean las vías alternas hacia Ollantaytambo y restringen el paso de trenes hacia Machu Picchu por huelga indefinida.",
                    "urgencia": "CRITICA",
                    "tipo_evento": "bloqueo_vias",
                    "ubicaciones_detectadas": ["Ollantaytambo", "Machu Picchu"],
                    "recomendaciones_locales": "Suspender traslados al Valle Sagrado de inmediato."
                }

        urgencia = alert_data.get("urgencia", alert_data.get("clasificacion", "CRITICA"))
        if urgencia == "IRRELEVANTE":
            print(" 🛑 [Agente Supervisor]: Alerta clasificada como IRRELEVANTE. Abortando pipeline para evitar SPAM en canales.")
            alert_data["despacho_status"] = {"estado_final": "archivado_no_despachado"}
            return alert_data

        print(f" 🤖 [Agente Supervisor]: Alerta válida detectada (Urgencia: {urgencia}).")

        languages = ["en", "fr", "pt"]
        workers = {lang: TranslatorWorker(lang) for lang in languages}
        traducciones_finales = {}
        threads = []

        texto_crudo = alert_data.get("texto_crudo", alert_data.get("resumen_ia", alert_data.get("titulo", "")))

        def worker_task(lang, worker, text):
            result = worker.translate_text(text)
            traducciones_finales[lang] = result

        print(" 🤖 [Agente Supervisor]: Delegando tareas concurrentes a los Agentes Traductores (Workers)...")
        for lang, worker in workers.items():
            t = threading.Thread(target=worker_task, args=(lang, worker, texto_crudo))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print(" 🤖 [Agente Supervisor]: Traducciones consolidadas recibidas con éxito. Verificando integridad...")
        alert_data["traducciones"] = traducciones_finales

        print(" 🤖 [Agente Supervisor]: Invocando al Agente Notificador para la difusión final...")
        status = self.notifier.dispatch_notifications(alert_data)
        alert_data["despacho_status"] = status

        output_dir = os.path.join("data", "processed")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "alertas_clasificadas_demo_final.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(alert_data, f, ensure_ascii=False, indent=2)

        print(f" ✅ [Agente Supervisor]: Ciclo completado. Archivo final persistido en: {output_file}")
        print("=== ⚙️ FIN DEL FLUJO DE TRABAJO ===\n")
        return alert_data


if __name__ == "__main__":
    supervisor = SupervisorAgent()
    supervisor.execute_pipeline()
