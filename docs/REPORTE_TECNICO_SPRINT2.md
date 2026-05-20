# CuscoNodes - Reporte Técnico del Módulo de Percepción (Sprint 2)

## 1. Estructura del Proyecto

Este informe describe el estado del repositorio en el cierre de Sprint 2, centrado en el **Módulo de Percepción**.

```text
cusconodes/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── scheduler.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── scrapers/
│       ├── __init__.py
│       ├── base_scraper.py
│       ├── rpp_scraper.py
│       ├── perurail_scraper.py
│       ├── perurail_announcement_scraper.py
│       └── alert_filter.py
├── data/
│   ├── raw/
│   │   ├── .gitkeep
│   │   ├── alertas_rpp_20260424_1922.json
│   │   ├── alertas_elcomercio_20260424_1922.json
│   │   ├── horarios_perurail_20260424_1922.json
│   │   ├── alertas_climaticas_20260424_1922.json
│   │   └── datos_cusco_relevantes_20260424_1922.json
│   └── processed/
│       ├── .gitkeep
│       ├── alertas_criticas_20260506_191152.json
│       └── resumen_alertas_20260506_*.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SPRINT2_FINAL.md
│   └── otros documentos de sprint y validación
├── tests/
│   └── test_scrapers.py
├── web_server.py
└── venv*/
```

### Función de cada componente principal

- `src/main.py`: punto de entrada del pipeline Sprint 2.
- `src/scheduler.py`: orquestador del flujo percepción → filtrado → persistencia → resumen.
- `src/scrapers/base_scraper.py`: clase abstracta común para todos los extractores.
- `src/scrapers/rpp_scraper.py`: extractor de noticias de RPP Cusco.
- `src/scrapers/perurail_scraper.py`: extractor de horarios/servicios de PeruRail.
- `src/scrapers/perurail_announcement_scraper.py`: extractor de avisos/suspensiones de PeruRail.
- `src/scrapers/alert_filter.py`: filtro heurístico que decide qué alertas son críticas para turistas.
- `src/config/settings.py`: centraliza variables de entorno, rutas y logging.
- `data/raw/`: persiste la salida sin procesar por scraper.
- `data/processed/`: persiste alertas filtradas y resúmenes ejecutivos.
- `tests/test_scrapers.py`: pruebas básicas de inicialización y retorno tipo lista.

### Dónde se guardan los outputs

- Raw por scraper: `data/raw/alertas_<nombre_scraper>_<timestamp>.json`.
- Alertas críticas: `data/processed/alertas_criticas_<timestamp>.json`.
- Resumen ejecutivo: `data/processed/resumen_alertas_<timestamp>.json`.

En los artefactos versionados del workspace también existen ejemplos históricos de validación:

- `data/raw/alertas_rpp_20260424_1922.json`
- `data/raw/alertas_elcomercio_20260424_1922.json`
- `data/raw/horarios_perurail_20260424_1922.json`
- `data/raw/alertas_climaticas_20260424_1922.json`
- `data/raw/datos_cusco_relevantes_20260424_1922.json`
- `data/processed/alertas_criticas_20260506_191152.json`
- `data/processed/resumen_alertas_20260506_*.json`

## 2. Pila Tecnológica y Dependencias

### Dependencias usadas directamente en el código del Sprint 2

| Librería | Uso en el proyecto |
|---|---|
| `requests` | Descarga HTML desde RPP y PeruRail con `timeout=10` y `raise_for_status()` |
| `beautifulsoup4` / `bs4` | Parseo de HTML con `BeautifulSoup(..., 'html.parser')` |
| `python-dotenv` | Carga de variables desde `.env` en `src/config/settings.py` |
| `flask` | Servidor local para servir el contenido web en `web_server.py` |

### Dependencias declaradas en `requirements.txt` pero no usadas de forma efectiva en el Sprint 2

| Librería | Presencia | Observación técnica |
|---|---|---|
| `selenium` | requirements | No aparece usada en el código de Sprint 2 |
| `lxml` | requirements | No se usa explícitamente; el parseo real usa `html.parser` |
| `pandas` | requirements | No se usa en el módulo de percepción |
| `APScheduler` | requirements | Referenciado como preparación para ejecución constante, pero no orquesta el Sprint 2 real |
| `openai` | requirements | Preparación para sprint futuro, sin uso en Sprint 2 |
| `google-generativeai` | requirements | Preparación para sprint futuro, sin uso en Sprint 2 |
| `SQLAlchemy` | requirements | No se usa en el código Sprint 2 |
| `pytest` / `pytest-cov` | requirements | Soporte de pruebas |
| `black`, `flake8`, `pylint` | requirements | Soporte de calidad de código |
| `python-dateutil`, `pytz` | requirements | Utilidades de fecha/hora disponibles para extensiones futuras |

### Módulos estándar de Python presentes

- `logging`
- `os`
- `json`
- `datetime`
- `pathlib.Path`
- `typing`
- `abc`

### Configuración y entorno

- `Settings.configure_logging()` activa el logging global con `logging.basicConfig(...)`.
- `Settings.DATA_STORAGE_PATH` define la raíz de persistencia, con valor por defecto `./data`.
- Variables relevantes en `.env.example` y `settings.py`:
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`
  - `GEMINI_API_KEY`
  - `RPP_URL`
  - `PERURAIL_URL`
  - `DATABASE_URL`
  - `SMTP_SERVER`
  - `SMTP_PORT`
  - `SENDER_EMAIL`
  - `DATA_STORAGE_PATH`
  - `PROJECT_ENV`
  - `LOG_LEVEL`

## 3. Módulo de Extracción (Scraping)

### 3.1 `BaseScraper`

Archivo: `src/scrapers/base_scraper.py`

Rol:

- Define la interfaz común del sistema de scraping.
- Obliga a implementar `scrape()` y `parse_article()`.
- Centraliza `save_to_json()` y `add_metadata()`.

Comportamiento clave:

- `add_metadata()` agrega automáticamente `fuente` y `fecha_scrape` si no existen.
- `save_to_json()` serializa una lista de diccionarios a JSON con `ensure_ascii=False` e `indent=2`.

### 3.2 `RPPScraper`

Archivo: `src/scrapers/rpp_scraper.py`

Fuente:

- URL base: `https://rpp.pe/cusco`

Selectores DOM principales:

- Lista de artículos: `soup.find_all('article', class_='article')`
- Título: `article.find('h2') or article.find('h3')`
- Enlace: `article.find('a')`

Lógica de extracción:

- Realiza `GET` con `requests`.
- Construye un `BeautifulSoup` con `html.parser`.
- Recorre cada `<article class="article">`.
- Toma el texto del primer `h2` o `h3` como `titulo`.
- Extrae `href` del primer enlace.
- Si el enlace es relativo, lo normaliza con prefijo `https://rpp.pe`.

Campos generados por cada registro:

- `titulo`: `str`
- `enlace`: `str`
- `fuente`: `str` (`"RPP Noticias Cusco"`)
- `tipo`: `str` (`"ALERTA"`)
- `fecha_scrape`: `str` en formato `YYYY-MM-DD HH:MM:SS`

### 3.3 `PeruRailScraper`

Archivo: `src/scrapers/perurail_scraper.py`

Fuente:

- URL base: `https://www.perurail.com`

Selectores DOM principales:

- Filas de horario: `soup.find_all('tr', class_='schedule-row')`
- Celdas: `article.find_all('td')`

Lógica de extracción:

- Descarga la página principal de PeruRail.
- Busca filas de tabla con clase `schedule-row`.
- Interpreta cada fila como un servicio ferroviario.
- Lee las columnas por índice en el orden fijo de la tabla.

Campos generados por cada registro:

- `servicio`: `str` (ej. `"03:20"`)
- `salida`: `str` (ej. `"Wanchaq"`)
- `llegada`: `str`
- `ruta`: `str` (ej. `"Expedition / Vistadome"`)
- `fecha_scrape`: `str` en formato `YYYY-MM-DD HH:MM:SS`

### 3.4 `PeruRailAnnouncementScraper`

Archivo: `src/scrapers/perurail_announcement_scraper.py`

Fuente:

- URL base: `https://www.perurail.com/es/noticias`

Selectores DOM principales:

- Bloques de avisos: `soup.find_all('div', class_=['announcement', 'alert', 'notice'])`
- Título: `article.find(['h2', 'h3', 'h4'])`
- Descripción: `article.find('p')`
- Fecha de publicación: `article.find(['span', 'time'], class_=['date', 'published'])`

Lógica de extracción:

- Descarga la sección de noticias de PeruRail.
- Busca bloques semánticamente parecidos a anuncios o alertas.
- Parsea cada bloque en un diccionario estructurado.
- Aplica un filtro semántico por palabras clave de suspensión.
- Clasifica ruta afectada, tipo de suspensión y urgencia.

Palabras clave de suspensión:

- `suspensión`, `suspendido`, `suspendida`
- `cancelado`, `cancelada`, `cancelados`
- `parado`, `paro`, `huelga`
- `cierre`, `cerrado`, `clausurado`
- `mantenimiento`, `reparación`
- `servicio no disponible`, `fuera de servicio`

Funciones internas importantes:

- `_is_suspension()` valida si el texto describe una suspensión real.
- `_extract_route()` intenta identificar rutas como `Cusco-Machu Picchu`, `Ollantaytambo`, `Wanchaq`, `Hidroeléctrica`, `Poroy`, `San Pedro`.
- `_categorize_suspension()` asigna categorías como `PARO_LABORAL`, `MANTENIMIENTO`, `CONDICIONES_CLIMATICAS`, `EMERGENCIA`, `OTRA`.
- `_calculate_urgency()` devuelve `URGENTE`, `ALTA` o `NORMAL`.

Campos generados por cada registro:

- `titulo`: `str`
- `descripcion`: `str`
- `fecha_publicacion`: `str`
- `ruta_afectada`: `str`
- `tipo_suspension`: `str`
- `urgencia`: `str`
- `fuente`: `str` (`"PeruRail Avisos Servicio"`)
- `tipo`: `str` (`"SUSPENSION"`)
- `fecha_scrape`: `str` en formato `YYYY-MM-DD HH:MM:SS`

### 3.5 `AlertFilter`

Archivo: `src/scrapers/alert_filter.py`

Este módulo no extrae HTML; procesa las alertas ya extraídas.

Función principal:

- `filter_critical_alerts(alerts)` recorre la lista y conserva solo alertas críticas para turistas.

Criterios de criticidad:

- Palabras clave de impacto turístico.
- Ubicaciones críticas (`Cusco`, `Machu Picchu`, `Ollantaytambo`, `Aguas Calientes`, `Vinicunca`, `Sacred Valley`).
- Urgencia `URGENTE` o `ALTA`.
- Tipo de alerta `SUSPENSION`, `ALERTA` o `EMERGENCIA`.
- Deduplicación temporal configurada por `dedup_hours=6`.

Campos que agrega al resultado filtrado:

- `criticidad`: `float` entre `0` y `100`
- `relevancia_turistica`: `str` (`"ALTA"`)

Función de resumen:

- `generate_summary(critical_alerts)` devuelve un resumen ejecutivo con totales por criticidad, tipo, ubicaciones afectadas y fuentes.

## 4. Esquema de Datos (Output JSON)

### 4.1 Salida raw de RPP

Archivo típico: `data/raw/alertas_rpp_<timestamp>.json`

Esquema por elemento:

```json
{
  "titulo": "string",
  "enlace": "string",
  "fuente": "string",
  "tipo": "string",
  "fecha_scrape": "string"
}
```

Notas:

- `titulo` puede venir de `h2` o `h3`.
- `enlace` puede ser absoluto porque el scraper normaliza enlaces relativos.
- `fecha_scrape` se genera en formato `YYYY-MM-DD HH:MM:SS`.

### 4.2 Salida raw de PeruRail horarios

Archivo típico: `data/raw/alertas_perurail_horarios_<timestamp>.json`

Esquema por elemento:

```json
{
  "servicio": "string",
  "salida": "string",
  "llegada": "string",
  "ruta": "string",
  "fecha_scrape": "string"
}
```

Ejemplo observado en `horarios_perurail_20260424_1922.json`:

- `servicio`: `"03:20"`
- `salida`: `"Wanchaq"`
- `llegada`: `""`
- `ruta`: `"Expedition"`
- `fecha_scrape`: `"2026-04-24 19:22:34"`

### 4.3 Salida raw de PeruRail avisos/suspensiones

Archivo típico: `data/raw/alertas_perurail_avisos_servicio_<timestamp>.json`

Esquema por elemento:

```json
{
  "titulo": "string",
  "descripcion": "string",
  "fecha_publicacion": "string",
  "ruta_afectada": "string",
  "tipo_suspension": "string",
  "urgencia": "string",
  "fuente": "string",
  "tipo": "string",
  "fecha_scrape": "string"
}
```

### 4.4 Salida procesada de alertas críticas

Archivo típico: `data/processed/alertas_criticas_<timestamp>.json`

El pipeline guarda una lista de alertas filtradas. Cada elemento conserva los campos originales y añade:

```json
{
  "titulo": "string",
  "enlace": "string",
  "fuente": "string",
  "tipo": "string",
  "fecha_scrape": "string",
  "criticidad": 0.0,
  "relevancia_turistica": "ALTA"
}
```

Cuando la alerta proviene del scraper de PeruRail de suspensiones, también puede conservar:

- `descripcion`
- `fecha_publicacion`
- `ruta_afectada`
- `tipo_suspension`
- `urgencia`

### 4.5 Resumen ejecutivo

Archivo típico: `data/processed/resumen_alertas_<timestamp>.json`

Esquema:

```json
{
  "total_alertas_criticas": 0,
  "fecha_generacion": "string",
  "alertas_por_criticidad": {
    "critica": 0,
    "alta": 0,
    "media": 0
  },
  "alertas_por_tipo": {
    "ALERTA": 0,
    "SUSPENSION": 0
  },
  "ubicaciones_afectadas": ["string"],
  "fuentes": ["string"]
}
```

### 4.6 Artefactos históricos de validación

El workspace contiene ejemplos reales de las estructuras anteriores:

- `data/raw/alertas_rpp_20260424_1922.json`
- `data/raw/alertas_elcomercio_20260424_1922.json`
- `data/raw/horarios_perurail_20260424_1922.json`
- `data/raw/datos_cusco_relevantes_20260424_1922.json`
- `data/raw/alertas_climaticas_20260424_1922.json`
- `data/processed/alertas_criticas_20260506_191152.json`

## 5. Flujo de Ejecución y Clases/Funciones Clave

### Archivo principal de ejecución

- `src/main.py`

### Secuencia de ejecución

1. `Settings.configure_logging()` inicializa el logger global.
2. Se instancian los scrapers:
   - `RPPScraper()`
   - `PeruRailScraper()`
   - `PeruRailAnnouncementScraper()`
3. Se instancia `AlertFilter(dedup_hours=6)`.
4. Se crea `CuscoNodesScheduler(data_path=Settings.DATA_STORAGE_PATH)`.
5. Se llama `scheduler.run_full_pipeline(scrapers, alert_filter)`.
6. El scheduler:
   - ejecuta `scraper.scrape()` para cada fuente,
   - persiste raw con `_save_raw_data()`,
   - filtra con `filter_critical_alerts()`,
   - persiste procesados con `_save_processed_data()`,
   - genera el resumen con `_save_summary()`.
7. `main()` imprime métricas finales:
   - `status`
   - `total_alerts_raw`
   - `total_alerts_critical`
   - cantidad de archivos creados
8. Si hay alertas críticas, `scheduler.get_latest_critical_alerts(limit=5)` lee el último JSON procesado y extrae las más recientes.

### Clases y funciones clave

#### `src/main.py`

- `main()`: orquesta todo el Sprint 2.

#### `src/scheduler.py`

- `CuscoNodesScheduler`: clase central del pipeline.
- `run_full_pipeline(scrapers, alert_filter)`: ejecuta percepción, filtrado, persistencia y resumen.
- `_save_raw_data(scraper_name, data)`: escribe el JSON sin procesar.
- `_save_processed_data(critical_alerts)`: escribe el JSON de alertas críticas.
- `_save_summary(summary)`: escribe el resumen ejecutivo.
- `get_latest_critical_alerts(limit)`: recupera las alertas más recientes desde `data/processed`.

#### `src/scrapers/base_scraper.py`

- `BaseScraper`: contrato base.
- `scrape()`: abstracto.
- `parse_article()`: abstracto.
- `add_metadata()`: agrega `fuente` y `fecha_scrape`.

#### `src/scrapers/rpp_scraper.py`

- `RPPScraper.scrape()`: descarga y parsea la sección Cusco.
- `RPPScraper.parse_article()`: extrae `titulo` y `enlace`.

#### `src/scrapers/perurail_scraper.py`

- `PeruRailScraper.scrape()`: lee horarios desde la tabla principal.
- `PeruRailScraper.parse_article()`: transforma la fila HTML en un registro estructurado.

#### `src/scrapers/perurail_announcement_scraper.py`

- `PeruRailAnnouncementScraper.scrape()`: detecta avisos y los filtra por suspensión.
- `parse_article()`: construye el objeto de aviso.
- `_is_suspension()`, `_extract_route()`, `_categorize_suspension()`, `_calculate_urgency()`: heurísticas de percepción semántica.

#### `src/scrapers/alert_filter.py`

- `filter_critical_alerts()`: selecciona alertas turísticas críticas.
- `_is_critical_for_tourists()`: regla principal de negocio.
- `_is_duplicate_recent()`: deduplicación temporal.
- `_calculate_criticality()`: score 0-100.
- `generate_summary()`: agregación final del estado del día.

### Observación técnica importante

- El `__init__.py` del paquete principal expone `CuscoNodesScheduler`, los tres scrapers y `AlertFilter`, por lo que el consumo del módulo está pensado como API de paquete, no como scripts sueltos.
- La versión declarada del paquete es `0.1.0-sprint2`.
- Aunque `selenium` está en dependencias, el Sprint 2 opera con scraping HTTP + BeautifulSoup, no con navegador automatizado.

---

## Resumen Ejecutivo para Sprint 3

El estado del Sprint 2 deja un pipeline determinista y auditable: múltiples scrapers producen listas de diccionarios normalizados, `AlertFilter` los reduce a señales críticas y `CuscoNodesScheduler` persiste el resultado en dos capas (`raw` y `processed`) con nombres de archivo timestamped. El sistema ya ofrece una base clara para introducir razonamiento semántico en Sprint 3 sin romper la capa de percepción.