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
- **Sprint 5:** Integración y Panel de Administración (planeado)
- **Sprint 6:** Pruebas y Cierre (planeado)

## Estado Actual (Post-Sprint 4)
- CUN-16 a CUN-21: 100% completado
- Pipeline real: Gemini API (traducción) → SMTP Gmail → Twilio WhatsApp
- Dashboard dinámico sin mocks, con historial y consulta IA
- Despliegue en Render pendiente (build conflict fix en bcaff3d)

## Archivos Relevantes
- `web_server.py` - Backend Flask con endpoints REST
- `web/index.html` - Dashboard frontend
- `src/multi_agent_orchestrator.py` - Pipeline Supervisor-Worker
- `src/config/settings.py` - Config de entorno
- `requirements.txt` - Dependencias
- `.python-version` - Python 3.12.6 para Render

## Endpoints REST
| Método | Endpoint | Función |
|--------|----------|---------|
| GET | `/` | Dashboard |
| POST | `/api/orchestrate` | Pipeline agentes |
| GET | `/api/history` | Historial ejecuciones |
| POST | `/api/query` | Consulta IA turismo |
| GET/POST | `/api/recipients` | CRUD destinatarios |

## Decisiones Técnicas Clave
- `google.genai` en lugar de `google.generativeai` (deprecado)
- Toponimias sagradas protegidas: Machu Picchu, Ollantaytambo, Sacsayhuamán, Pisac, Chinchero, Urubamba
- `data/recipients.json` para destinatarios dinámicos
- Python 3.12.6 fijado para compatibilidad Render
- Render free tier duerme tras 15 min; primera visita ~30s

## Critical Context
- **Gemini API:** Cuota gratuita excedida (429). Traducciones caen a fallback. Se requiere billing.
- **Twilio WhatsApp:** Solo números que hayan enviado `join step-till` al `+14155238886`.
- **SMTP:** Funciona con Contraseña de Aplicación de Gmail.
- **Twilio Sandbox:** Sender fijo `whatsapp:+14155238886`.
- **Render format:** Usar `.python-version` (NO `runtime.txt`) para fijar versión Python.
