# REPORTE TÉCNICO — SPRINT 4
## CuscoNodes: Épica 3 — Acción y Comunicación (CUN-16 a CUN-21)
**Fecha:** 3 de junio de 2026
**Versión:** 0.1.0-sprint4

---

## 1. Resumen Ejecutivo

El Sprint 4 migró el pipeline de agentes Supervisor-Worker de mocks locales a APIs reales (Gemini, SMTP y Twilio WhatsApp), incorporó un sistema de consultas a la IA (CUN-19), e implementó plantillas HTML profesionales de alerta (CUN-21). El 100% de las historias de la Épica 3 están completadas y funcionales.

| Historia | Estado | % |
|---|---|---|
| CUN-16 — Traducción multilingüe con Gemini API | ✅ | 100% |
| CUN-17 — Agentes cooperativos Supervisor-Worker | ✅ | 100% |
| CUN-18 — Despacho de notificaciones multicanal | ✅ | 100% |
| CUN-19 — Preguntas a la IA | ✅ | 100% |
| CUN-20 — Twilio WhatsApp + SMTP real | ✅ | 100% |
| CUN-21 — Plantillas de alerta HTML | ✅ | 100% |

---

## 2. Flujo de Trabajo de los Agentes (Pipeline)

El sistema ejecuta un pipeline secuencial de 4 etapas, cada una a cargo de un agente especializado:

```
1. SupervisorAgent
     ↓ lee alerta desde data/processed/
2. TranslatorWorker (EN) ──┐
   TranslatorWorker (FR) ──┤── concurrente (threading)
   TranslatorWorker (PT) ──┘
     ↓ consolida traducciones
3. NotifierWorker
     ├── SMTP (Gmail real)
     └── Twilio WhatsApp (real)
     ↓ persiste resultado
4. data/processed/alertas_clasificadas_demo_final.json
```

### 2.1 Etapa 1 — SupervisorAgent (orquestador)

```
🤖 [Agente Supervisor]: Monitoreando directorio local 'data/processed/'...
🤖 [Agente Supervisor]: Archivo detectado -> alertas_clasificadas_demo_*.json
🤖 [Agente Supervisor]: Alerta válida detectada (Urgencia: CRÍTICA).
🤖 [Agente Supervisor]: Delegando tareas concurrentes a los Agentes Traductores...
```

El `SupervisorAgent` es el **orquestador central**. Lee el archivo JSON más reciente del directorio `data/processed/`, extrae el campo `texto_crudo` (o `resumen_ia`) y crea 3 workers de traducción en **hilos paralelos**. Si la alerta es `IRRELEVANTE`, aborta el pipeline para evitar SPAM.

**Comportamiento clave:** el Supervisor no traduce ni notifica — solo gobierna el flujo y decide qué workers invocar.

### 2.2 Etapa 2 — TranslatorWorker × 3 (concurrentes)

```
🔠 [Agente Traductor - EN]: Invocando Gemini API para traducción contextual...
🔠 [Agente Traductor - FR]: Invocando Gemini API para traducción contextual...
🔠 [Agente Traductor - PT]: Invocando Gemini API para traducción contextual...
  (0.5s de stagger entre cada uno para evitar rate limiting)

⏳ [Agente Traductor - EN]: Cuota excedida, reintentando en 1s... (intento 1/3)
⏳ [Agente Traductor - EN]: Cuota excedida, reintentando en 2s... (intento 2/3)
⏳ [Agente Traductor - EN]: Cuota excedida, reintentando en 4s... (intento 3/3)
⚠️ [Agente Traductor - EN]: Máximos reintentos agotados. Usando fallback.
  o
✅ [Agente Traductor - EN]: Traducción recibida de Gemini.
```

Cada `TranslatorWorker`:
1. Envía el texto original a Gemini API con un **System Prompt** que ordena preservar los 6 topónimos sagrados sin traducir (Machu Picchu, Ollantaytambo, Sacsayhuamán, Pisac, Chinchero, Urubamba)
2. Espera la respuesta JSON con 3 campos: `titulo`, `contenido`, `recomendaciones`
3. Si hay error de cuota (429), reintenta con backoff exponencial: 1s → 2s → 4s
4. Si todos los reintentos fallan, usa **fallback** con traducciones predefinidas
5. Se ejecutan en paralelo gracias a `threading.Thread`

**Comportamiento clave:** los 3 workers se lanzan con 0.5s de diferencia (stagger) y corren simultáneamente. Cada uno es independiente — si uno falla, los otros dos no se ven afectados.

### 2.3 Etapa 3 — NotifierWorker (despacho dual)

```
📨 [Agente Notificador]: Analizando payload enriquecido multilingüe...
📧 [Agente Notificador] -> Conectando a smtp.gmail.com:587...
✅ [Agente Notificador] -> Correo enviado exitosamente a honoriomorales.t@gmail.com
📱 [Agente Notificador] -> [Twilio WhatsApp]: Enviando a +51922466959...
✅ [Agente Notificador] -> WhatsApp enviado (SID: SMf4989e4c8713d8defe08e5cb3d6874e0)
```

El `NotifierWorker` recibe el payload completo (texto original + traducciones) y ejecuta **2 envíos independientes**:

| Canal | Tecnología | Estado |
|---|---|---|
| **Email** | `smtplib` + Gmail SMTP | ✅ Real — construye HTML con las 3 traducciones en tarjetas con banderas |
| **WhatsApp** | `twilio.rest.Client` + Sandbox | ✅ Real — envía mensaje Markdown con alerta y traducciones |

Cada canal reporta su éxito individual en `despacho_status`:
- `whatsapp_intentos: 1` / `smtp_intentos: 1` si funcionaron
- `estado_final: "despachado"` si al menos uno funcionó
- `estado_final: "fallido_cola"` si ambos fallaron

**Comportamiento clave:** los canales son independientes — si SMTP falla, WhatsApp igual se intenta, y viceversa. El pipeline nunca crashea por un fallo de envío.

### 2.4 Etapa 4 — Persistencia

```
✅ [Agente Supervisor]: Ciclo completado. Archivo persistido en data/processed/alertas_clasificadas_demo_final.json
```

El resultado completo se guarda en JSON con toda la estructura: alerta original, traducciones, estado de despacho, y métricas de latencia.

---

## 3. Endpoints REST

| Endpoint | Método | Función |
|---|---|---|
| `http://127.0.0.1:5000/` | GET | Dashboard web (frontend) |
| `POST /api/orchestrate` | POST | Ejecuta el pipeline completo de agentes |
| `GET /api/history` | GET | Últimas 20 ejecuciones registradas |
| `POST /api/query` | POST | Consulta a la IA sobre turismo en Cusco |
| `GET /api/recipients` | GET | Obtiene destinatarios actuales (WhatsApp y email) |
| `POST /api/recipients` | POST | Actualiza destinatarios de alertas |

---

## 4. Capturas de Evidencia (por historia)

### CUN-16 — Traducción con Gemini
1. Terminal — `[Agente Traductor - EN] Invocando Gemini API...` junto con los otros 2 idiomas
2. Terminal — `✅ Traducción recibida de Gemini` (cuando hay cuota) o `⚠️ Usando fallback`
3. `data/processed/alertas_clasificadas_demo_final.json` — campo `traducciones` con EN, FR, PT

### CUN-17 — Agentes Cooperativos
4. Terminal completa — las 4 etapas visibles: Supervisor → 3 Workers → Notifier → Persistencia
5. Dashboard — tarjetas de Supervisor, Traductor y Notificador mostrando estado FINALIZADO / VALIDADO

### CUN-18 — Despacho SMTP
6. Terminal — `📧 Conectando a smtp.gmail.com:587... ✅ Correo enviado exitosamente`
7. Gmail — correo recibido con el HTML renderizado (alerta roja + 3 tarjetas de traducción)

### CUN-19 — Preguntas a la IA
8. Dashboard — panel "Consulta a la IA" con una pregunta escrita y la respuesta visible
9. `curl` o Postman — `POST /api/query` con `{"question":"..."}` → respuesta 200 JSON

### CUN-20 — Twilio WhatsApp
10. Terminal — `📱 [Twilio WhatsApp]: ✅ WhatsApp enviado (SID: SM...)`
11. Celular — mensaje de WhatsApp recibido con la alerta y traducciones

### CUN-21 — Plantillas HTML + Dashboard
12. Gmail — captura del HTML mostrando las banderas 🇬🇧 🇫🇷 🇧🇷 y toponimias destacadas
13. Dashboard — tabla de historial con hora, urgencia, texto, traducciones, estado y latencia
14. Dashboard — panel de métricas con latencia del proceso y `DESPACHADO`
15. Dashboard — panel "Destinatarios de Alerta" con los números/correos configurados

---

## 5. Guía rápida de captura

```bash
# 1. Iniciar servidor
cd ~/IA/cusconodes && source .venv/bin/activate && python web_server.py

# 2. Abrir en navegador
# http://127.0.0.1:5000

# 3. Hacer clic en "Ejecutar Orquestación de Agentes"

# 4. Para ver logs completos en terminal (sin前端):
python src/multi_agent_orchestrator.py

# 5. Para probar API directo:
curl -X POST http://127.0.0.1:5000/api/orchestrate
curl -X POST http://127.0.0.1:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Qué rutas están bloqueadas?"}'
```
