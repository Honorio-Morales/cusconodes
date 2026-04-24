# Arquitectura del Sistema CuscoNodes

## Pipeline Agéntico de Percepción (Sprint 2)

### Diagrama del Flujo

```
┌─────────────────────────────────────────────────────────────┐
│        MÓDULO DE PERCEPCIÓN - SPRINT 2                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Fuentes Locales │
├──────────────────┤
│ • RPP Noticias   │
│ • PeruRail       │
│ • OTROS (Future) │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│  Base Scraper            │
│  (Clase Abstracta)       │
│  - scrape()              │
│  - parse_article()       │
│  - save_to_json()        │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │          │
    ▼          ▼
┌─────────┐ ┌──────────────┐
│ RPP     │ │ PeruRail     │
│ Scraper │ │ Scraper      │
└────┬────┘ └──────┬───────┘
     │             │
     └─────┬───────┘
           ▼
    ┌────────────────┐
    │ JSON Storage   │
    │ /data/raw/     │
    └────────┬───────┘
             │
             ▼
    [Listos para Sprint 3]
```

### Componentes Principales

#### 1. BaseScraper
- Clase abstracta que define la interfaz común
- Métodos: `scrape()`, `parse_article()`, `save_to_json()`, `add_metadata()`
- Manejo centralizado de logging y errores

#### 2. RPPScraper
- Especializado en RPP Noticias - Sección Cusco
- Extrae: título, descripción, URL
- Filtrado para noticias relevantes para turistas

#### 3. PeruRailScraper
- Especializado en comunicados de PeruRail
- Extrae: cambios de horarios, cierres, avisos operacionales
- Crítico para turistas que toman el tren

### Estructura de Datos JSON

```json
{
  "title": "String - Título de la noticia",
  "description": "String - Descripción o resumen",
  "url": "String - URL de la fuente",
  "source": "String - Nombre del scraper (RPP/PeruRail)",
  "scraped_at": "ISO DateTime - Fecha de extracción",
  "type": "String - Tipo: article/announcement"
}
```

### Flujo de Ejecución

1. **Inicialización**: Cargar variables de `.env`
2. **Scraping**: Ejecutar scrapers paralelos
3. **Parseo**: Estructurar datos extraídos
4. **Almacenamiento**: Guardar en `/data/raw/*.json`
5. **Metadatos**: Agregar timestamp y fuente

---

## Próximos Pasos (Sprint 3)

- Integración con OpenAI/Gemini API
- Clasificación de incidentes por urgencia
- Filtrado automático de noticias irrelevantes

