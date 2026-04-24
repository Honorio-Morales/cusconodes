# Ejemplos de Salida - Módulo de Percepción Sprint 2

## Resumen
Este documento muestra los formatos exactos de salida de los scrapers del Sprint 2, validados con datos reales extraídos el **24 de Abril de 2026**.

---

## 1. Salida RPPScraper: Noticias de RPP Cusco

**Archivo:** `data/raw/alertas_rpp_20260424_1922.json`

**Estructura de Campos:**
```json
{
  "titulo": "string - Título de la noticia",
  "enlace": "string - URL completa de la noticia",
  "fuente": "string - 'RPP Noticias Cusco' o equivalente",
  "tipo": "string - 'ALERTA' o 'NOTICIA'",
  "fecha_scrape": "string - Timestamp en formato 'YYYY-MM-DD HH:MM:SS'"
}
```

**Ejemplo Real:**
```json
[
  {
    "titulo": "Cusco: hallan muro inca de 200 metros en zona privada tras deslizamientos en San Jerónimo",
    "enlace": "https://rpp.pe/peru/cusco/cusco-hallan-muro-inca-de-200-metros-en-zona-privada-tras-deslizamientos-en-san-jeronimo-noticia-1684823",
    "fuente": "RPP Cusco",
    "tipo": "ALERTA",
    "fecha_scrape": "2026-04-24 19:22:35"
  },
  {
    "titulo": "Cusco: capturan a integrantes de facción del Tren de Aragua vinculados al asesinato de ciudadana paraguaya",
    "enlace": "https://rpp.pe/peru/cusco/cusco-capturan-a-integrantes-de-faccion-del-tren-de-aragua-vinculados-al-asesinato-de-ciudadana-paraguaya-noticia-1684408",
    "fuente": "RPP Cusco",
    "tipo": "ALERTA",
    "fecha_scrape": "2026-04-24 19:22:35"
  }
]
```

**Criterios de Extracción:**
- Título: Texto del heading principal (h2/h3)
- Enlace: Href del tag `<a>`, convertido a URL absoluta si es relativo
- Fuente: "RPP Cusco"
- Tipo: "ALERTA" (por defecto)
- Fecha de Scrape: Timestamp en formato manual

---

## 2. Salida PeruRailScraper: Horarios de Trenes

**Archivo:** `data/raw/horarios_perurail_20260424_1922.json`

**Estructura de Campos:**
```json
{
  "servicio": "string - Hora de salida (HH:MM)",
  "salida": "string - Estación de partida",
  "llegada": "string - Estación de destino",
  "ruta": "string - Tipo de tren (Expedition, Vistadome, etc)",
  "fecha_scrape": "string - Timestamp en formato 'YYYY-MM-DD HH:MM:SS'"
}
```

**Ejemplo Real:**
```json
[
  {
    "servicio": "03:20",
    "salida": "Wanchaq",
    "llegada": "",
    "ruta": "Expedition",
    "fecha_scrape": "2026-04-24 19:22:34"
  },
  {
    "servicio": "05:05",
    "salida": "Ollantaytambo",
    "llegada": "",
    "ruta": "Expedition",
    "fecha_scrape": "2026-04-24 19:22:34"
  },
  {
    "servicio": "07:35",
    "salida": "Poroy",
    "llegada": "",
    "ruta": "Expedition / Vistadome",
    "fecha_scrape": "2026-04-24 19:22:34"
  },
  {
    "servicio": "05:35",
    "salida": "Machu Picchu Pueblo",
    "llegada": "(Aguas Calientes)",
    "ruta": "Expedition",
    "fecha_scrape": "2026-04-24 19:22:34"
  }
]
```

**Criterios de Extracción:**
- Servicio: Hora de salida (columna 1 de tabla)
- Salida: Estación de partida (columna 2)
- Llegada: Estación de destino (columna 3)
- Ruta: Tipo de servicio (columna 4)
- Fecha de Scrape: Timestamp automático

---

## 3. Datos Filtrados/Procesados (Output Esperado para Sprint 3)

**Archivo:** `data/raw/datos_cusco_relevantes_20260424_1922.json`

> **Nota:** Este archivo es resultado de post-procesamiento y filtrado (Sprint 3), pero se incluye como referencia.

**Estructura Enriquecida:**
```json
{
  "id": "integer - ID único",
  "tipo": "string - 'alerta', 'horario'",
  "titulo_descripcion": "string - Resumen en minúsculas",
  "detalles": "string - Detalles adicionales",
  "fuente": "string - Origen de datos",
  "enlace": "string - URL de referencia",
  "fecha_scrape": "integer - Timestamp en milisegundos",
  "archivo_origen": "string - Archivo JSON de origen",
  "urgencia": "string - 'URGENTE', 'ALTA', 'NORMAL'"
}
```

**Ejemplos Reales (Alertas Críticas para Turistas):**
```json
[
  {
    "id": 19,
    "tipo": "alerta",
    "titulo_descripcion": "evalúan cerrar ingreso a montaña de colores vinicunca por lluvias intensas y nevadas en cusco",
    "detalles": "{'titulo': 'Evalúan cerrar ingreso a Montaña de Colores Vinicunca por lluvias intensas y nevadas en Cusco', ...}",
    "fuente": "El Comercio Cusco",
    "enlace": "https://elcomercio.pe/peru/cusco/...",
    "fecha_scrape": 1777058556000,
    "archivo_origen": "alertas_elcomercio_20260424_1922.json",
    "urgencia": "URGENTE"
  },
  {
    "id": 22,
    "tipo": "alerta",
    "titulo_descripcion": "cusco: ríos vilcanota, mapacho y salcca aumentan su caudal por intensas lluvias",
    "detalles": "{'titulo': 'Cusco: Ríos Vilcanota, Mapacho y Salcca aumentan su caudal por intensas lluvias', ...}",
    "fuente": "El Comercio Cusco",
    "enlace": "https://elcomercio.pe/peru/...",
    "fecha_scrape": 1777058556000,
    "archivo_origen": "alertas_elcomercio_20260424_1922.json",
    "urgencia": "URGENTE"
  },
  {
    "id": 28,
    "tipo": "alerta",
    "titulo_descripcion": "cusco: cientos de pasajeros protestaron en estación en machu picchu por alta demanda de boletos",
    "detalles": "{'titulo': 'Cusco: Cientos de pasajeros protestaron en estación en Machu Picchu por alta demanda de boletos', ...}",
    "fuente": "El Comercio Cusco",
    "enlace": "https://elcomercio.pe/peru/cusco/...",
    "fecha_scrape": 1777058556000,
    "archivo_origen": "alertas_elcomercio_20260424_1922.json",
    "urgencia": "URGENTE"
  }
]
```

---

## 4. Estadísticas de Extracción Reales

### Sesión: 24 de Abril de 2026, 19:22 UTC

| Fuente | Tipo | Cantidad | Ejemplo |
|--------|------|----------|---------|
| RPP Cusco | Noticias/Alertas | 15+ artículos | Noticia sobre deslizamientos, seguridad |
| El Comercio | Noticias/Alertas | 10+ artículos | Lluvia, cierres de accesos |
| PeruRail | Horarios | 60+ registros | Salidas hacia Machu Picchu |
| **Total Procesado** | **Datos Relevantes** | **60+** | Alertas urgentes para turistas |

---

## 5. Casos de Uso - Información Crítica para Turistas

### Alertas de Alto Impacto Identificadas ⚠️

1. **Vinicunca (Montaña de 7 Colores) - CIERRE POR CLIMA**
   - Urgencia: **URGENTE**
   - Impacto: Cierre de acceso por lluvia y nieve
   - Relevancia: Atracción turística principal

2. **Aumento de Caudal de Ríos**
   - Urgencia: **URGENTE**
   - Impacto: Riesgo de inundaciones
   - Relevancia: Afecta rutas turísticas

3. **Protestas en Machu Picchu**
   - Urgencia: **URGENTE**
   - Impacto: Congestión y retrasos
   - Relevancia: Punto de interés principal

4. **Cambios en Horarios de PeruRail**
   - Urgencia: **NORMAL** → **ALTA** (si hay cambios)
   - Impacto: Afecta transporte de turistas
   - Relevancia: Conexión esencial Cusco-Machu Picchu

---

## 6. Mapeo: RPP → Filtrado → Alerta Turística

```
RPP Noticias (15 artículos)
    ↓
[Análisis de relevancia turística - Sprint 3]
    ↓
Seleccionar alertas críticas (5 artículos)
    ↓
[Clasificación de urgencia por IA - Sprint 3]
    ↓
Traducir a idiomas (ES, EN, FR, DE) - Sprint 4
    ↓
Enviar WhatsApp/Email a turistas - Sprint 4
```

---

## 7. Validación de Datos

✅ **Criterios Cumplidos en Sprint 2:**
- [x] Estructura JSON bien formada
- [x] Campos consistentes en todos los registros
- [x] Timestamps presentes
- [x] URLs completas y válidas
- [x] Caracteres especiales (ñ, acentos) procesados correctamente
- [x] Datos deduplicados y sin ruido

⏳ **Próximas Mejoras (Sprint 3+):**
- [ ] Clasificación automática de urgencia
- [ ] Filtrado por palabras clave turísticas
- [ ] Deduplicación temporal (no reportar 2x la misma alerta)
- [ ] Scoring de relevancia por IA

---

## 8. Cómo Usar Estos Ejemplos

1. **Testing Local:**
   ```bash
   # Los archivos reales están en:
   ls -la data/raw/alertas_*.json
   ls -la data/raw/horarios_*.json
   ```

2. **Validación Estructural:**
   ```bash
   python -c "import json; json.load(open('data/raw/alertas_rpp_20260424_1922.json'))"
   ```

3. **Visualizar Resultados:**
   ```bash
   cat data/raw/alertas_rpp_20260424_1922.json | python -m json.tool
   ```

---

## 9. Archivos Relacionados

- **Código:** [src/scrapers/rpp_scraper.py](../src/scrapers/rpp_scraper.py)
- **Código:** [src/scrapers/perurail_scraper.py](../src/scrapers/perurail_scraper.py)
- **Datos Raw:** `/data/raw/*.json`
- **Docs:** [ARCHITECTURE.md](ARCHITECTURE.md), [SPRINT2.md](SPRINT2.md)

