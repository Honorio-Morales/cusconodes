# Descripciones de Tareas - Sprint 2 (Para Jira)

## Formato para Jira

Copia y pega estas descripciones en Jira cuando marques cada tarea como completada.

---

## ✅ CUN-12: Configuración Técnica

**Estado:** HECHO  
**Puntos:** 2  
**Responsable:** Honorio Morales

### Descripción Completa

**Objetivo:** Establecer la infraestructura técnica base del proyecto CuscoNodes en GitHub con Python y dependencias.

**Tareas Completadas:**
- [x] Crear repositorio GitHub: https://github.com/Honorio-Morales/cusconodes
- [x] Estructura de carpetas profesional (src/, data/, tests/, docs/)
- [x] Python 3.9+ configurado
- [x] Crear requirements.txt con 15+ dependencias
- [x] Crear .env.example con todas las variables necesarias
- [x] Crear .gitignore para Python y IDE
- [x] Crear README.md con instrucciones de instalación
- [x] Inicializar Git y hacer primer commit
- [x] Hacer push a GitHub

**Criterios de Aceptación:**
- ✅ Repositorio público en GitHub
- ✅ README con instrucciones funcionales
- ✅ requirements.txt con versiones pinned
- ✅ .env.example sin valores sensibles
- ✅ Estructura lista para desarrollo

**Notas Técnicas:**
```
- Framework: Python puro (sin framework web)
- Pattern: Abstract Base Class (ABC)
- Storage: JSON local (escalable a SQLAlchemy)
- Logging: módulo estándar logging
- Git: commits semánticos
```

**Entregables:**
- Repositorio GitHub funcional
- 7 documentos de referencia
- requirements.txt con dependencias
- .gitignore y .env.example

---

## ✅ CUN-13: Scraper RPP Cusco

**Estado:** HECHO  
**Puntos:** 3  
**Responsable:** Honorio Morales

### Descripción Completa

**Objetivo:** "Como sistema, quiero extraer noticias de rpp.pe/peru/cusco para identificar incidentes"

**Tareas Completadas:**
- [x] Crear clase `RPPScraper` que hereda de `BaseScraper`
- [x] Implementar método `scrape()` para HTTP GET + BeautifulSoup parsing
- [x] Implementar método `parse_article()` con estructura: `{titulo, enlace, fuente, tipo, fecha_scrape}`
- [x] Agregar conversión de URLs relativas a absolutas
- [x] Agregar manejo de errores y logging
- [x] Implementar retry logic con timeout=10s
- [x] Validar con 15 artículos reales del 24-Abr-2026

**Estructura de Salida:**
```json
{
  "titulo": "string - Título de la noticia",
  "enlace": "string - URL completa",
  "fuente": "string - 'RPP Cusco'",
  "tipo": "string - 'ALERTA' o 'NOTICIA'",
  "fecha_scrape": "string - 'YYYY-MM-DD HH:MM:SS'"
}
```

**Criterios de Aceptación:**
- ✅ Extrae datos sin errores
- ✅ URLs convertidas a absolutas
- ✅ Maneja timeouts correctamente
- ✅ Logging detallado
- ✅ Datos guardados en JSON
- ✅ Validado con datos reales (15+ artículos)

**Datos Reales Validados:**
- Ubicación: RPP Noticias Cusco
- Registros: 15 artículos
- Fecha: 24-Abr-2026 19:22
- Archivo: `data/raw/alertas_rpp_20260424_1922.json`
- Ejemplos: Deslizamientos, seguridad, noticias

---

## ✅ CUN-14: Scraper PeruRail

**Estado:** HECHO  
**Puntos:** 3  
**Responsable:** Honorio Morales

### Descripción Completa

**Objetivo:** "Como sistema, quiero monitorear avisos de PeruRail para detectar suspensiones de trenes"

**Tareas Completadas:**
- [x] Crear clase base `PeruRailScraper` para horarios
- [x] Crear clase `PeruRailAnnouncementScraper` para suspensiones/avisos
- [x] Método `scrape()` extrae horarios y avisos
- [x] Método `parse_article()` parsea: `{servicio, salida, llegada, ruta, fecha_scrape}`
- [x] Método `_is_suspension()` detecta palabras clave de suspensión
- [x] Método `_categorize_suspension()` clasifica: PARO_LABORAL, MANTENIMIENTO, etc.
- [x] Método `_calculate_urgency()` determina: URGENTE, ALTA, NORMAL
- [x] Validar con 60+ horarios reales del 24-Abr-2026

**Estructura de Salida (Horarios):**
```json
{
  "servicio": "string - Hora de salida (HH:MM)",
  "salida": "string - Estación de partida",
  "llegada": "string - Estación destino",
  "ruta": "string - Tipo de tren (Expedition, Vistadome)",
  "fecha_scrape": "string - 'YYYY-MM-DD HH:MM:SS'"
}
```

**Estructura de Salida (Avisos de Suspensión):**
```json
{
  "titulo": "string",
  "descripcion": "string",
  "ruta_afectada": "string - Cusco-Machu Picchu, etc",
  "tipo_suspension": "string - PARO_LABORAL, MANTENIMIENTO, CLIMA",
  "urgencia": "string - URGENTE, ALTA, NORMAL",
  "fecha_scrape": "string"
}
```

**Criterios de Aceptación:**
- ✅ Extrae horarios correctamente
- ✅ Detecta suspensiones por palabras clave
- ✅ Clasifica tipo de suspensión
- ✅ Calcula urgencia automáticamente
- ✅ Maneja rutas múltiples (Wanchaq, Ollantaytambo, etc)
- ✅ Validado con datos reales (60+ registros)

**Datos Reales Validados:**
- Ubicación: PeruRail
- Horarios: 60+ registros
- Estaciones: Wanchaq, Ollantaytambo, Machu Picchu, Hidroeléctrica
- Fecha: 24-Abr-2026 19:22
- Archivo: `data/raw/horarios_perurail_20260424_1922.json`

---

## ✅ CUN-15: Base de Datos Local

**Estado:** HECHO  
**Puntos:** 2  
**Responsable:** Honorio Morales

### Descripción Completa

**Objetivo:** "Implementar el archivo alertas_raw.json para guardar las extracciones locales"

**Tareas Completadas:**
- [x] Crear método `save_to_json()` en `BaseScraper`
- [x] Almacenamiento en `/data/raw/` con estructura de carpetas
- [x] Implementar `add_metadata()` para timestamp y fuente
- [x] Deduplicación automática de IDs
- [x] Integrar datos reales: 4 archivos JSON
- [x] Crear `CuscoNodesScheduler` para orquestación
- [x] Validar estructura de datos
- [x] Documentar formato de almacenamiento

**Estructura de Directorios:**
```
/data/
├── raw/                    # Datos sin procesar
│   ├── alertas_rpp_20260424_1922.json
│   ├── alertas_elcomercio_20260424_1922.json
│   ├── horarios_perurail_20260424_1922.json
│   ├── alertas_climaticas_20260424_1922.json
│   └── datos_cusco_relevantes_20260424_1922.json
└── processed/              # Datos filtrados y procesados
    └── [Generado en Sprint 3]
```

**Datos Almacenados:**
- RPP Cusco: 15 artículos
- El Comercio: 10+ artículos
- PeruRail: 60+ horarios
- Alertas Climáticas: 200+ registros
- Datos Procesados: 60+ alertas críticas (referencia)

**Criterios de Aceptación:**
- ✅ Archivos JSON bien formados
- ✅ Caracteres especiales (ñ, acentos) procesados
- ✅ Estructura consistente
- ✅ Timestamps presentes
- ✅ Datos sin ruido ni duplicados
- ✅ Path de almacenamiento configurable

**Notas Técnicas:**
```python
# Estructura genérica (configurable por scraper)
{
  "titulo/servicio": "...",
  "descripcion/enlace": "...",
  "fuente": "...",
  "fecha_scrape": "...",
  # ... campos adicionales específicos
}
```

---

## ✅ CUN-16: Sistema de Filtrado (NUEVO - Sprint 2 Final)

**Estado:** HECHO  
**Puntos:** 3  
**Responsable:** Honorio Morales

### Descripción Completa

**Objetivo:** "Filtrar automáticamente alertas críticas relevantes para turistas de Cusco"

**Tareas Completadas:**
- [x] Crear clase `AlertFilter` con criterios de filtrado
- [x] Identificar palabras clave de impacto turístico (Machu Picchu, tren, etc)
- [x] Filtrar por ubicación crítica (Cusco, Ollantaytambo, Aguas Calientes)
- [x] Deduplicación temporal (no alertar 2x en 6 horas)
- [x] Calcular score de criticidad (0-100)
- [x] Generar resumen ejecutivo de alertas
- [x] Integrar en pipeline principal

**Criterios de Filtrado:**
1. **Palabras Clave Turísticas:** Machu Picchu, tren, vías, atracciones
2. **Ubicación:** Solo Cusco y zonas turísticas
3. **Urgencia:** URGENTE o ALTA
4. **Deduplicación:** No repetir en 6 horas
5. **Tipo:** Suspensiones, emergencias, alertas críticas

**Score de Criticidad:**
```
URGENTE + SUSPENSION = 80-100
ALTA + RUTA_AFECTADA = 60-79
NORMAL + INFORMACIÓN = 40-59
```

**Entregables:**
```json
{
  "titulo": "...",
  "fuente": "...",
  "criticidad": 85.5,
  "relevancia_turistica": "ALTA",
  "urgencia": "URGENTE"
}
```

---

## ✅ CUN-17: Scheduler & Ejecución Constante (NUEVO - Sprint 2 Final)

**Estado:** HECHO  
**Puntos:** 3  
**Responsable:** Honorio Morales

### Descripción Completa

**Objetivo:** "Permitir que el sistema se ejecute constantemente y genere reportes automáticos"

**Tareas Completadas:**
- [x] Crear clase `CuscoNodesScheduler` para orquestación
- [x] Método `run_full_pipeline()` para flujo completo
- [x] Ejecutar scrapers en secuencia
- [x] Aplicar filtrado automático
- [x] Guardar datos raw + procesados
- [x] Generar resumen executivo
- [x] Logging detallado de cada paso
- [x] Manejo de errores por scraper

**Pipeline:**
```
1. Ejecutar RPPScraper → 15 artículos
2. Ejecutar PeruRailScraper → 60+ horarios
3. Ejecutar PeruRailAnnouncementScraper → suspensiones
4. Filtrar alertas críticas → AlertFilter
5. Guardar datos raw → /data/raw/
6. Guardar datos procesados → /data/processed/
7. Generar resumen → /data/processed/resumen_*.json
```

**Configuración para Ejecución Constante (Future):**
```python
# Con APScheduler (configurar en Sprint 3)
scheduler = BackgroundScheduler()
scheduler.add_job(
    pipeline.run_full_pipeline,
    'interval',
    minutes=30  # Ejecutar cada 30 minutos
)
scheduler.start()
```

**Entregables:**
- Scheduler funcional
- Logging de cada fase
- Manejo de errores
- Timestamps automáticos
- Archivos timestamped

---

## 📋 Comentario General para Jira

```
Sprint 2 - Módulo de Percepción: 100% Completado ✅

Status de Tareas:
✅ CUN-12: Configuración Técnica
✅ CUN-13: Scraper RPP Cusco
✅ CUN-14: Scraper PeruRail
✅ CUN-15: Base de Datos Local
✅ CUN-16: Sistema de Filtrado (PLUS)
✅ CUN-17: Scheduler & Ejecución (PLUS)

Datos Validados:
- 15 artículos RPP Cusco
- 10+ artículos El Comercio
- 60+ horarios PeruRail
- 200+ registros climáticos
- Arquitectura profesional con ABC pattern

Documentación:
- 8 documentos de referencia
- Ejemplos reales de salida
- Guía de arquitectura
- Reporte formal de cierre

GitHub: https://github.com/Honorio-Morales/cusconodes
Tag: sprint-2-percepcion

Próximo: Sprint 3 - Motor de Razonamiento (IA + Clasificación)
```

---

## Próximos Pasos para Jira

1. **Mover cada tarea a DONE:**
   - CUN-12 → DONE
   - CUN-13 → DONE
   - CUN-14 → DONE
   - CUN-15 → DONE

2. **Hacer click en "Completar Sprint"**

3. **Crear Sprint 3 con tareas:**
   - CUN-18: Integración OpenAI API
   - CUN-19: Clasificador de Urgencia
   - CUN-20: Motor de Traducción
   - CUN-21: Integración WhatsApp/Email
