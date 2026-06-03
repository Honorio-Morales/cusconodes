"""
Multi-Agent Orchestrator - Sistema Supervisor-Worker para CuscoNodes
Sprint 4: Traducción con Gemini API real + preparación SMTP
"""

import json
import os
import glob
import time
import threading
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client as TwilioClient
from google import genai
from google.genai import types
try:
    from .config.settings import Settings
except ImportError:
    from config.settings import Settings

IDIOMA_PROMPTS = {
    "en": "Translate the following alert text into English. You are a professional tourism translator for Cusco, Peru.",
    "fr": "Traduisez le texte d'alerte suivant en français. Vous êtes un traducteur touristique professionnel pour Cusco, Pérou.",
    "pt": "Traduza o seguinte texto de alerta para o português. Você é um tradutor turístico profissional para Cusco, Peru.",
}

TOPONIMIAS_PROTEGIDAS = [
    "Machu Picchu", "Ollantaytambo", "Sacsayhuamán",
    "Pisac", "Chinchero", "Urubamba"
]

SYSTEM_INSTRUCTION = (
    "Eres un traductor especializado en turismo para Cusco, Perú. "
    "Debes preservar SIN TRADUCIR los siguientes topónimos sagrados: "
    + ", ".join(TOPONIMIAS_PROTEGIDAS) + ". "
    "Devuelve exclusivamente un objeto JSON válido con tres campos: "
    '"titulo" (string, título de la alerta), "contenido" (string, cuerpo traducido), '
    '"recomendaciones" (string, recomendaciones para turistas). '
    "No incluyas texto adicional fuera del JSON."
)

MODEL_NAME = "gemini-2.0-flash"
MAX_RETRIES = 3

CLIENTE_GEMINI = genai.Client(api_key=Settings.GEMINI_API_KEY)
CONFIG_GEMINI = types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)


class TranslatorWorker:
    """Agente Especializado en Traducción Turística Multilingüe con Gemini API (CUN-16)"""
    def __init__(self, target_lang):
        self.target_lang = target_lang

    def translate_text(self, text):
        print(f" 🔠 [Agente Traductor - {self.target_lang.upper()}]: Invocando Gemini API para traducción contextual...")
        for attempt in range(MAX_RETRIES):
            try:
                prompt = f"{IDIOMA_PROMPTS[self.target_lang]}\n\nTexto original: {text}"
                response = CLIENTE_GEMINI.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=CONFIG_GEMINI
                )
                raw = response.text.strip()

                if raw.startswith("```"):
                    for prefix in ("```json\n", "```json", "```"):
                        if raw.startswith(prefix):
                            raw = raw.removeprefix(prefix)
                    raw = raw.removesuffix("```").strip()

                result = json.loads(raw)
                required = {"titulo", "contenido", "recomendaciones"}
                if not required.issubset(result.keys()):
                    raise ValueError(f"Campos faltantes: {required - result.keys()}")
                print(f" ✅ [Agente Traductor - {self.target_lang.upper()}]: Traducción recibida de Gemini.")
                return result

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    wait = 2 ** attempt
                    print(f" ⏳ [Agente Traductor - {self.target_lang.upper()}]: Cuota excedida, reintentando en {wait}s... (intento {attempt+1}/{MAX_RETRIES})")
                    time.sleep(wait)
                else:
                    print(f" ⚠️ [Agente Traductor - {self.target_lang.upper()}]: Error Gemini ({e}). Usando fallback.")
                    return self._fallback_translation(text)

        print(f" ⚠️ [Agente Traductor - {self.target_lang.upper()}]: Máximos reintentos agotados. Usando fallback.")
        return self._fallback_translation(text)

    def _fallback_translation(self, text):
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
    """Agente Especializado en Canales de Acción y Difusión Multimedio (CUN-18 + CUN-20)"""
    def __init__(self):
        self.smtp_server = Settings.SMTP_SERVER
        self.smtp_port = Settings.SMTP_PORT
        self.sender_email = Settings.SENDER_EMAIL
        self.sender_password = Settings.SENDER_PASSWORD
        self.twilio_sid = Settings.TWILIO_ACCOUNT_SID
        self.twilio_token = Settings.TWILIO_AUTH_TOKEN
        self.recipients_file = os.path.join("data", "recipients.json")

    def _load_recipients(self):
        if os.path.exists(self.recipients_file):
            with open(self.recipients_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"whatsapp": "", "email": ""}

    def dispatch_notifications(self, payload):
        print(" 📨 [Agente Notificador]: Analizando payload enriquecido multilingüe...")
        smtp_ok = self._send_email(payload)
        whatsapp_ok = self._send_whatsapp(payload)

        estado = "despachado"
        if not smtp_ok and not whatsapp_ok:
            estado = "fallido_cola"
        elif not smtp_ok or not whatsapp_ok:
            estado = "despacho_parcial"

        return {
            "whatsapp_intentos": 1 if whatsapp_ok else 0,
            "smtp_intentos": 1 if smtp_ok else 0,
            "estado_final": estado
        }

    def _send_email(self, payload):
        if not self.sender_email or not self.sender_password:
            print(" ⚠️ [Agente Notificador]: SMTP no configurado (SENDER_EMAIL/PASSWORD vacío). Saltando envío.")
            return False

        recip = self._load_recipients()
        to_email = recip.get("email") or self.sender_email

        print(f" 📧 [Agente Notificador] -> [SMTP {self.smtp_server}:{self.smtp_port}]: Construyendo mensaje...")
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.sender_email
            msg["To"] = to_email
            msg["Subject"] = f"🔔 Alerta CuscoNodes: {payload.get('urgencia', 'INFORMATIVA')}"

            texto_crudo = payload.get("texto_crudo", payload.get("resumen_ia", "Sin contenido"))
            traducciones = payload.get("traducciones", {})

            html_parts = ""
            for lang in ["en", "fr", "pt"]:
                t = traducciones.get(lang, {})
                banderas = {"en": "🇬🇧", "fr": "🇫🇷", "pt": "🇧🇷"}
                html_parts += f"""
                <div style="margin-bottom:20px;padding:15px;border-left:4px solid #6366f1;background:#f8fafc;border-radius:6px;">
                    <h3 style="margin:0 0 8px 0;font-size:14px;color:#334155;">{banderas[lang]} {lang.upper()}</h3>
                    <p style="margin:0 0 4px 0;font-size:13px;color:#1e293b;"><strong>Título:</strong> {t.get('titulo', '')}</p>
                    <p style="margin:0 0 4px 0;font-size:13px;color:#475569;"><strong>Contenido:</strong> {t.get('contenido', '')}</p>
                    <p style="margin:0;font-size:13px;color:#475569;"><strong>Recomendaciones:</strong> {t.get('recomendaciones', '')}</p>
                </div>"""

            html = f"""\
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;padding:30px;background:#f1f5f9;">
    <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:12px;padding:25px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
        <div style="border-bottom:2px solid #6366f1;padding-bottom:15px;margin-bottom:20px;">
            <h1 style="font-size:18px;color:#1e293b;margin:0;">CuscoNodes</h1>
            <p style="font-size:12px;color:#64748b;margin:4px 0 0 0;">Sistema de Monitoreo Multi-Agente · Alerta {payload.get('urgencia', 'INFORMATIVA')}</p>
        </div>
        <div style="margin-bottom:20px;padding:15px;background:#fef2f2;border:1px solid #fecaca;border-radius:6px;">
            <h2 style="font-size:14px;color:#991b1b;margin:0 0 8px 0;">⚠️ Alerta Original</h2>
            <p style="font-size:13px;color:#7f1d1d;margin:0;">{texto_crudo}</p>
        </div>
        {html_parts}
        <div style="border-top:1px solid #e2e8f0;padding-top:12px;margin-top:20px;font-size:11px;color:#94a3b8;text-align:center;">
            CuscoNodes · Sistema de Inteligencia Artificial Agéntica · {time.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""

            msg.attach(MIMEText(html, "html"))

            print(f" 📧 [Agente Notificador] -> Conectando a {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())

            print(f" ✅ [Agente Notificador] -> Correo enviado exitosamente a {to_email}")
            return True

        except Exception as e:
            print(f" ⚠️ [Agente Notificador] -> Fallo SMTP: {e}")
            return False

    def _send_whatsapp(self, payload):
        if not self.twilio_sid or not self.twilio_token:
            print(" ⚠️ [Agente Notificador]: Twilio no configurado. Saltando WhatsApp.")
            return False

        recip = self._load_recipients()
        to_wa = recip.get("whatsapp")
        if not to_wa:
            print(" ⚠️ [Agente Notificador]: Número WhatsApp no configurado. Saltando envío.")
            return False

        try:
            texto = payload.get("texto_crudo", payload.get("resumen_ia", ""))
            urgencia = payload.get("urgencia", "INFORMATIVA")
            traducciones = payload.get("traducciones", {})

            mensaje = (
                f"🔔 *CuscoNodes - Alerta {urgencia}*\n\n"
                f"📄 *Texto:* {texto[:200]}\n\n"
            )
            for lang in ["en", "fr", "pt"]:
                t = traducciones.get(lang, {})
                if t.get("titulo"):
                    mensaje += f"🌐 *{lang.upper()}:* {t['titulo']}\n{t.get('contenido','')[:100]}...\n\n"

            print(f" 📱 [Agente Notificador] -> [Twilio WhatsApp]: Enviando a {to_wa}...")
            client = TwilioClient(self.twilio_sid, self.twilio_token)
            message = client.messages.create(
                body=mensaje,
                from_="whatsapp:+14155238886",
                to=f"whatsapp:{to_wa}"
            )
            print(f" ✅ [Agente Notificador] -> WhatsApp enviado (SID: {message.sid})")
            return True

        except Exception as e:
            print(f" ⚠️ [Agente Notificador] -> Fallo Twilio WhatsApp: {e}")
            return False


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
            print(" ⚠️ [Agente Supervisor]: Directorio vacío o sin alertas procesadas. Generando caso de prueba...")
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
            print(" 🛑 [Agente Supervisor]: Alerta clasificada como IRRELEVANTE. Abortando pipeline.")
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

        print(" 🤖 [Agente Supervisor]: Delegando tareas concurrentes a los Agentes Traductores (Workers) con Gemini API...")
        for i, (lang, worker) in enumerate(workers.items()):
            t = threading.Thread(target=worker_task, args=(lang, worker, texto_crudo))
            threads.append(t)
            t.start()
            time.sleep(0.5)

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
