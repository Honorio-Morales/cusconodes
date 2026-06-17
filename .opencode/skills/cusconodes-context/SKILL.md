---
name: cusconodes-context
description: >
  Use when discussing CuscoNodes project status, sprints, architecture, or
  technical decisions. Covers Sprint 2-4, pipeline de agentes, endpoints REST,
  dashboard, y configuración de despliegue. Use ONLY for CuscoNodes project context.
---

# CuscoNodes — Contexto del Proyecto

## Descripción General
Sistema de IA agéntica para alertas turísticas en Cusco. Pipeline de 3 etapas: Percepción (scraping) → Razonamiento (IA) → Acción (notificación multicanal).

## Equipo
- PM/Dev: Honorio Morales Ttito
- PO: Sebastian Zavaleta Luna
- SM: Sayo Michael Torres Caceres
- Sponsor: Israel Rondán (PDS Viajes)

## Timeline de Sprints
- **Sprint 1:** Iniciación ✅
- **Sprint 2:** Percepción (scraping) ✅
- **Sprint 3:** Razonamiento (agentes mock + dashboard) ✅
- **Sprint 4:** Acción (APIs reales: Gemini, SMTP, Twilio) ✅
- **Sprint 5:** Integración y Administración ✅ (completado)
  - CUN-22: Autenticación básica (login con contraseña única)
  - CUN-23: Despliegue Render funcional (health check, .python-version)
  - CUN-24: Panel de métricas (Chart.js, tasa éxito, latencia promedio)
  - CUN-25: Exportación CSV del historial
  - CUN-26: Scheduler automático (APScheduler con control start/stop)
  - Plan de monitoreo: health endpoint, logs, tracking de ejecuciones
- **Sprint 6:** Pruebas y Cierre (pendiente)

## Estado Actual (Post-Sprint 5)
- Pipeline real: Gemini API (traducción) → SMTP Gmail → Twilio WhatsApp
- Dashboard con login protegido, métricas en tiempo real, gráfico de alertas/día
- Scheduler automático configurable desde el panel
- Exportación de historial a CSV
- Monitoreo de pipeline con tracking de éxito/fallo
- URLs de API relativas (funciona en local y Render sin cambios)

## Archivos Relevantes
- `web_server.py` - Backend Flask con endpoints REST (auth, metrics, scheduler, monitoring, export)
- `web/index.html` - Dashboard frontend con login overlay, Chart.js, controles scheduler
- `src/multi_agent_orchestrator.py` - Pipeline Supervisor-Worker
- `src/config/settings.py` - Config de entorno
- `requirements.txt` - Dependencias
- `.python-version` - Python 3.12.6 para Render
- `.env.example` - Template con variables ADMIN_PASSWORD y FLASK_SECRET_KEY

## Endpoints REST
| Método | Endpoint | Función | Auth |
|--------|----------|---------|------|
| GET | `/` | Dashboard | No |
| GET | `/api/health` | Health check | No |
| POST | `/api/login` | Login | No |
| POST | `/api/logout` | Logout | No |
| GET | `/api/auth/status` | Verificar sesión | No |
| POST | `/api/orchestrate` | Pipeline agentes | Sí |
| GET | `/api/history` | Historial (50) | Sí |
| GET | `/api/metrics` | Métricas agregadas | Sí |
| GET | `/api/export/csv` | Descargar CSV | Sí |
| POST | `/api/query` | Consulta IA turismo | No |
| GET/POST | `/api/recipients` | CRUD destinatarios | Sí |
| POST | `/api/scheduler/start` | Iniciar scheduler | Sí |
| POST | `/api/scheduler/stop` | Detener scheduler | Sí |
| GET | `/api/scheduler/status` | Estado scheduler | Sí |
| GET | `/api/monitoring` | Estadísticas pipeline | Sí |

## Decisiones Técnicas Clave
- `google.genai` en lugar de `google.generativeai` (deprecado)
- Toponimias sagradas protegidas: Machu Picchu, Ollantaytambo, Sacsayhuamán, Pisac, Chinchero, Urubamba
- `data/recipients.json` para destinatarios dinámicos
- Autenticación por sesión Flask (no JWT, sin BD de usuarios)
- Chart.js v4 desde CDN para gráfico de barras
- Scheduler vía APScheduler BackgroundScheduler en mismo proceso
- URLs relativas en frontend (sin hardcodear 127.0.0.1:5000)
- Python 3.12.6 fijado para compatibilidad Render
- Render free tier duerme tras 15 min; primera visita ~30s

## Critical Context
- **Gemini API:** Cuota gratuita excedida (429). Traducciones caen a fallback. Se requiere billing.
- **Twilio WhatsApp:** Solo números que hayan enviado `join step-till` al `+14155238886`.
- **SMTP:** Funciona con Contraseña de Aplicación de Gmail.
- **Twilio Sandbox:** Sender fijo `whatsapp:+14155238886`.
- **Render format:** Usar `.python-version` (NO `runtime.txt`) para fijar versión Python.
- **ADMIN_PASSWORD:** Por defecto `cusconodes2025`. Cambiar en `.env` o variable de entorno de Render.
- **FLASK_SECRET_KEY:** Generar una aleatoria para producción. Sin ella, las sesiones se invalidan al reiniciar.
