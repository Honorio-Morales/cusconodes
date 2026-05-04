# CuscoNodes - Sistema de Inteligencia Artificial Agéntica

**Sistema de alertas inteligente para turistas en Cusco**

## 📋 Descripción del Proyecto

CuscoNodes es un sistema de IA agéntica diseñado para transformar la experiencia del turista en la región de Cusco, proporcionando alertas en tiempo real sobre incidentes locales (huelgas, cierres de vías, clima) en su idioma nativo.

### Pipeline Agéntico (3 Etapas):
1. **Percepción** (scraping de fuentes locales)
2. **Razonamiento** (análisis por IA)
3. **Acción** (traducción y notificación multicanal)

---

## 🏗️ Estructura del Proyecto

```
cusconodes/
├── src/
│   ├── scrapers/           # Módulos de extracción de datos
│   │   ├── base_scraper.py
│   │   ├── rpp_scraper.py
│   │   └── perurail_scraper.py
│   ├── config/             # Configuración del proyecto
│   │   └── settings.py
│   └── main.py             # Orquestador principal
├── data/
│   ├── raw/                # Datos sin procesar (JSON)
│   └── processed/          # Datos procesados
├── tests/                  # Suite de pruebas
├── docs/                   # Documentación del proyecto
├── requirements.txt        # Dependencias Python
├── .env.example           # Variables de entorno (plantilla)
└── .gitignore            # Archivos ignorados por Git
```

---

## 🚀 Configuración del Entorno

### Requisitos Previos
- Python 3.9+
- Git
- pip

### Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/Honorio-Morales/cusconodes.git
cd cusconodes
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus valores
```

---

## 📋 Sprint 2: Módulo de Percepción

**Objetivo:** Tener scripts funcionales de extracción de datos.

### Tareas Completadas
- [x] Estructura del proyecto creada
- [x] Configuración del entorno Python
- [x] Scraper para RPP Noticias Cusco
- [x] Scraper para comunicados de PeruRail
- [x] Base de datos local en formato JSON
- [x] Filtrado de alertas críticas con scoring y deduplicación
- [x] Scheduler para ejecución continua

### Estado Consolidado

Sprint 2 está **completado al 100%**. El módulo de percepción ya integra scraping, almacenamiento, filtrado y programación de ejecución, con datos reales validados y documentación de cierre disponible.

### Listo para Sprint 3

La base técnica necesaria para continuar ya está presente:
- datos reales en `data/raw/`
- alertas procesadas en `data/processed/`
- `AlertFilter` para clasificación inicial
- `CuscoNodesScheduler` para orquestación
- tests básicos y estructura de configuración
- documentación de cierre en `docs/SPRINT2_FINAL.md`

---

## 👥 Equipo del Proyecto

| Rol | Responsable |
|-----|-----------|
| Project Manager / Dev | Honorio Morales Ttito |
| Product Owner | Sebastian Zavaleta Luna |
| Scrum Master | Sayo Michael Torres Caceres |
| Patrocinador | Israel Rondán (PDS Viajes) |

---

## 📅 Timeline

- **Sprint 1:** Iniciación y Planificación ✅ (Finalizado)
- **Sprint 2:** Módulo de Percepción ✅ (Finalizado)
- **Sprint 3:** Motor de Razonamiento
- **Sprint 4:** Acción y Comunicación
- **Sprint 5:** Integración y Panel de Administración
- **Sprint 6:** Pruebas y Cierre

---

## 📝 Licencia

Proyecto académico - PDS Viajes

