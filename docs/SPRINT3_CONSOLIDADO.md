# Sprint 3: Motor de Razonamiento - Consolidado desde Acta de Constitución

**Fecha de Análisis:** 4 de Mayo de 2026  
**Fuente:** Acta de Constitución del Proyecto + Estado actual de Sprint 2  
**Estado del Proyecto:** 50% completado (Percepción lista, Razonamiento próximo)

---

## 📋 Pipeline Agéntico General (Acta de Constitución)

```
┌─────────────────────────────────────────────────────────┐
│   CUSCONODES: Sistema de IA Agéntica para Turismo      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ETAPA 1: PERCEPCIÓN (Sprint 2) ✅ COMPLETADO           │
│   ├─ Scraping de fuentes locales                       │
│   │  ├─ RPP Noticias Cusco                             │
│   │  ├─ El Comercio (edición Cusco)                    │
│   │  ├─ PeruRail                                       │
│   │  └─ Portal oficial de Machu Picchu                 │
│   └─ Almacenamiento en JSON local (/data/raw/)         │
│                                                         │
│ ETAPA 2: RAZONAMIENTO (Sprint 3) 🔄 EN CURSO           │
│   ├─ Integración API LLM (OpenAI/Gemini)               │
│   ├─ Filtrado por relevancia turística                 │
│   ├─ Clasificación por urgencia (CRÍTICA, INFO, IRRELEVANTE)│
│   └─ Salida procesada (/data/processed/)               │
│                                                         │
│ ETAPA 3: ACCIÓN (Sprint 4) ⏳ PLANEADO                  │
│   ├─ Motor de traducción multilingüe                   │
│   │  ├─ Inglés, Francés, Alemán                        │
│   │  ├─ Portugués, Mandarín, Japonés                   │
│   ├─ Envío por Email                                   │
│   ├─ Envío por WhatsApp Business API                   │
│   └─ Panel de administración básico                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ SPRINT 2 - PERCEPCIÓN (COMPLETADO)

### Tareas Ejecutadas (6/6)
- [x] **CUN-12**: Configuración técnica del repo y estructura
- [x] **CUN-13**: RPPScraper con 15+ artículos validados
- [x] **CUN-14**: PeruRailScraper con 60+ horarios validados
- [x] **CUN-15**: Base de datos local en JSON
- [x] **CUN-16**: AlertFilter (scoring, deduplicación, urgencia inicial)
- [x] **CUN-17**: CuscoNodesScheduler (orquestador del pipeline)

### Componentes Funcionales
```python
src/scrapers/
├── base_scraper.py                    # Clase abstracta
├── rpp_scraper.py                     # RPP Noticias
├── perurail_scraper.py                # Horarios PeruRail
├── perurail_announcement_scraper.py   # Anuncios PeruRail
├── alert_filter.py                    # Filtrado inicial
└── __init__.py

src/scheduler.py                       # Orquestación CuscoNodesScheduler
src/main.py                            # Ejecutor principal
src/config/settings.py                 # Configuración centralizada
```

### Output Generado
- **Raw Data:** `data/raw/` → alertas_rpp, alertas_elcomercio, horarios_perurail, alertas_climaticas
- **Processed Data:** `data/processed/` → alertas_criticas (con scoring básico)
- **Total de registros validados:** 345+ (datos reales del 24-Abr-2026)

### Criterios de Aceptación Sprint 2 ✅
- [x] Sistema monitorea fuentes locales de forma autónoma
- [x] Agente ejecuta ciclos de percepción (preparado para cada 60 minutos)
- [x] Almacenamiento en JSON con metadatos completos
- [x] Datos validados con fuentes reales

---

## 🔄 SPRINT 3 - RAZONAMIENTO (PRÓXIMO)

### Objetivo según Acta
> "Agente de razonamiento que filtra y clasifica la información según relevancia turística y nivel de urgencia, donde un agente LLM determina si una noticia es Crítica, Informativa o Irrelevante"

**Timeline según Acta:** Semana 5–6 (mediados a finales de mayo)

### Tareas Definidas en Acta (Mapeadas)

| ID Acta | Descripción | Estado | Input | Output |
|---------|-------------|--------|-------|--------|
| Hito 5-6 | Agente de razonamiento integrado | ⏳ No iniciado | `/data/raw/*.json` | `/data/processed/alertas_clasificadas.json` |

### Tareas Técnicas Desglosadas (Propuesta)

#### **CUN-18: Integración API LLM**
- **Objetivo:** Conectar OpenAI o Gemini API
- **Criterio de Aceptación:**
  - [x] Variable `LLM_API_KEY` en `.env.example`
  - [x] Código puede conectar y obtener respuesta
  - [x] Manejo de errores y rate limiting
- **Owner:** Honorio Morales
- **Story Points:** 5

#### **CUN-19: Clasificador de Urgencia (IA)**
- **Objetivo:** Implementar prompt engineering para clasificación 3-niveles
- **Criterio de Aceptación:**
  - [x] Todos los registros clasificados como CRÍTICA, INFORMATIVA o IRRELEVANTE
  - [x] Validación: 0 falsas alarmas en 100 registros de prueba
  - [x] Scoring de confianza (0-100) en cada clasificación
- **Owner:** Sebastian Zavaleta
- **Story Points:** 8
- **Prompt Base:**
```
Eres un clasificador de alertas turísticas para Cusco. 
Clasifica esta noticia como:
- CRÍTICA: Afecta seguridad/acceso directo (huelgas, cierres, clima extremo)
- INFORMATIVA: Útil pero no urgente (eventos culturales, cambios menores)
- IRRELEVANTE: Sin impacto turístico

Entrada: {titulo} - {descripcion}
Output JSON: {"categoria": "CRÍTICA|INFORMATIVA|IRRELEVANTE", "confianza": 0-100, "razón": "..."}
```

#### **CUN-20: Filtro de Relevancia Turística**
- **Objetivo:** Aplicar contexto turístico (ubicaciones, rutas, sitios arqueológicos)
- **Criterio de Aceptación:**
  - [x] Reconoce ubicaciones clave: Machu Picchu, Ollantaytambo, Valle Sagrado, Plaza de Armas
  - [x] Detecta tipos de eventos relevantes (cierres, huelgas, restricciones, clima)
  - [x] Genera resumen ejecutivo para agencia
- **Owner:** Sayo Michael Torres
- **Story Points:** 5

#### **CUN-21: Pipeline Integrado (Sprint 3)**
- **Objetivo:** Conectar Percepción → Razonamiento → Almacenamiento
- **Criterio de Aceptación:**
  - [x] `CuscoNodesScheduler` ejecuta full pipeline sin manual intervention
  - [x] Output: `/data/processed/alertas_clasificadas_{timestamp}.json`
  - [x] Logging detallado de cada etapa
- **Owner:** Honorio Morales
- **Story Points:** 3

---

## 🎯 Requisitos de Alto Nivel (Acta) → Sprint 3

### Requisito 1: Monitoreo Autónomo
```
Status en Sprint 2: ✅ LISTO
  El scheduler ejecuta cada 60 minutos sin intervención
  
Status en Sprint 3: 🔄 EXTENDER
  Agregar razonamiento en cada ciclo (no solo percepción)
  Input: alertas raw + output: alertas clasificadas
```

### Requisito 2: Clasificación por Relevancia
```
Status en Sprint 2: ⚠️ PARCIAL (reglas heurísticas)
  AlertFilter usa keywords y scoring simple
  
Status en Sprint 3: ✅ MEJORAR
  Usar LLM para clasificación semántica real
  Reducir falsas alarmas
  Agregar contexto turístico
```

### Requisito 3: Idioma Nativo del Turista
```
Status en Sprint 2: ⏳ PREPARACIÓN
  Estructura lista para multiidioma
  
Status en Sprint 3: ⏳ PREPARACIÓN  
  Motor de traducción será Sprint 4
  Pero Sprint 3 debe dejar lista la salida para traducción
```

---

## 📊 Datos de Entrada Disponibles para Sprint 3

Generados en Sprint 2, listos para procesar:

```
/data/raw/
├── alertas_rpp_20260424_1922.json          (15 artículos)
├── alertas_elcomercio_20260424_1922.json   (10+ artículos)
├── horarios_perurail_20260424_1922.json    (60+ horarios)
├── alertas_climaticas_20260424_1922.json   (200+ registros)
└── datos_cusco_relevantes_20260424_1922.json (60+ datos procesados)

Total: 345+ registros reales para clasificación
```

### Estructura Esperada del Input
```json
{
  "titulo": "PeruRail suspende trenes a Machu Picchu por huelga",
  "enlace": "https://...",
  "fuente": "RPP Cusco",
  "tipo": "ALERTA",
  "fecha_scrape": "2026-04-24 19:22:35"
}
```

### Estructura Esperada del Output (Sprint 3)
```json
{
  "id": 1,
  "titulo": "PeruRail suspende trenes a Machu Picchu por huelga",
  "fuente": "RPP Cusco",
  "clasificacion": "CRÍTICA",
  "confianza": 95,
  "ubicaciones": ["Machu Picchu", "Ollantaytambo"],
  "tipo_evento": "cierre_transporte",
  "resumen_ia": "Suspensión indefinida de servicios de tren hacia Machu Picchu...",
  "recomendacion": "Avisar inmediatamente a turistas con viajes programados",
  "fecha_scrape": "2026-04-24 19:22:35"
}
```

---

## 🌐 Interfaz Web Existente (Avance SzavaletaL)

**Ubicación:** `/web/`

### Componentes Actuales
- [x] **Frontend:** HTML + Tailwind CSS con dashboard responsivo
  - Tarjetas de noticias por categoría
  - Selector de idioma (EN, ES, FR, DE, PT, ZH, JA)
  - Botones de compartir por WhatsApp/Email
  - Badge de "IA Agéntica Activa"

- [x] **Backend parcial:** `web/scripts/scrapyng.py`
  - Scrapers integrados (similar a Sprint 2 pero independiente)
  - Clasificación por heurísticas simples
  - Normalización de datos

### Limitación Actual
- Usa **reglas hardcodeadas**, no LLM
- No está integrada con el pipeline `src/scheduler.py`
- Es un prototipo desacoplado de la arquitectura principal

### Integración Propuesta para Sprint 3
```
Sprint 3 Output: /data/processed/alertas_clasificadas.json
          ↓
       API REST (agregar en Sprint 3 o 4)
          ↓
    /web/index.html (consume API)
          ↓
   Dashboard visual (ya listo)
```

---

## 📝 Hitos y Timeline (Acta + Realidad)

| Semana | Hito Acta | Sprint | Status |
|--------|-----------|--------|--------|
| 1–2 | Acta aprobada, backlog | - | ✅ Completado |
| 3–4 | Módulo de percepción con 3+ fuentes | 2 | ✅ Completado |
| 5–6 | Agente de razonamiento integrado | 3 | 🔄 **ESTA SEMANA** |
| 7–8 | Motor de traducción + envío | 4 | ⏳ Próximo |
| 9–10 | Panel de admin básico | 5 | ⏳ Próximo |
| 11–12 | Pruebas, ajustes, demo final | 5 | ⏳ Próximo |

**Nota:** Hoy es 4 de mayo (día 1 de la semana objetivo para Sprint 3).

---

## 🔐 Riesgos Identificados en Acta (Aplicables a Sprint 3)

| Riesgo | Mitigación Sprint 3 |
|--------|-------------------|
| Cambios en HTML de fuentes rompen scrapers | Scrapers ya validados en Sprint 2; Sprint 3 no toca eso |
| Restricciones API WhatsApp | No aplica a Sprint 3 (es etapa de Acción) |
| Carga académica paralela | Planificar 5-8 story points por persona |
| APIs externas con interrupciones | Usar modelo local como fallback o cache |
| Costo de APIs LLM | Usar free tier OpenAI / Gemini API gratuita |

---

## ✨ Conclusión: Sprint 3 en Contexto

**Sprint 2 entregó:** Percepciones automáticas y almacenadas.  
**Sprint 3 debe entregar:** Razonamiento que convierte percepciones en decisiones inteligentes.  

Actualmente:
- El pipeline de percepción está **100% funcional**
- Los datos están **listos para clasificación**
- La interfaz web **existe pero desacoplada**
- El LLM debe **conectarse e integrarse ahora**

**Meta Sprint 3:** Que `CuscoNodesScheduler` ejecute cada 60 minutos y genere alertas clasificadas por urgencia, sin falsas alarmas, listas para enviar al turista en la etapa siguiente.

---

*Documento consolidado: 4 de Mayo de 2026*  
*Análisis cruzado: Acta de Constitución + Estado Sprint 2 + Propuesta Sprint 3*
