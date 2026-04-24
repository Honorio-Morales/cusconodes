# Changelog

Todas las notas sobre cambios importantes en este proyecto serán documentadas en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-sprint2] - 2026-04-24

### 🎉 Lanzamiento Sprint 2: Módulo de Percepción

**Línea de Base:** Sistema operativo de scraping con arquitectura ABC, datos validados.

### Added

#### Componentes Core
- `BaseScraper` - Clase abstracta base para todos los scrapers con interfaz común
  - `scrape()` - Método abstracto para extracción de datos
  - `parse_article()` - Método abstracto para parseo de elementos
  - `save_to_json()` - Persistencia de datos en JSON
  - `add_metadata()` - Enriquecimiento automático de registros
  - Logging centralizado con manejo de errores robusto

- `RPPScraper` - Extractor especializado para RPP Noticias Cusco
  - Extrae: `{titulo, enlace, fuente, tipo, fecha_scrape}`
  - Validado con 15 artículos reales (24-Abr-2026)
  - Conversión de URLs relativas a absolutas
  - Manejo de timeouts y reintentos

- `PeruRailScraper` - Extractor especializado para horarios de PeruRail
  - Extrae: `{servicio, salida, llegada, ruta, fecha_scrape}`
  - Validado con 60+ registros reales (24-Abr-2026)
  - Soporte para tablas con múltiples secciones
  - Parsing robusto de formatos variados

#### Sistema de Configuración
- `Settings` - Gestión centralizada de variables de entorno
  - Soporte para `python-dotenv`
  - Configuración de API keys (OpenAI, Gemini)
  - Rutas de almacenamiento configurables
  - Logging automático

- `.env.example` - Plantilla de variables de entorno
  - Documentación de cada variable
  - Valores por defecto sensatos

#### Suite de Pruebas
- `tests/test_scrapers.py` - Tests unitarios básicos
  - TestRPPScraper: Validación de inicialización y structure
  - TestPeruRailScraper: Validación de inicialización y structure
  - Extensible para agregar más tests

#### Documentación
- `README.md` - Guía de inicio rápido
  - Descripción del proyecto
  - Instrucciones de instalación
  - Estructura del proyecto
  - Timeline de sprints

- `ARCHITECTURE.md` - Diseño de sistema
  - Diagrama ASCII del pipeline
  - Descripción de componentes
  - Estructura de datos JSON
  - Próximos pasos

- `SPRINT2.md` - Tareas y checklist del sprint
  - Tareas completadas
  - Tareas pendientes
  - Cómo usar la estructura
  - Notas técnicas

- `EJEMPLOS_SALIDA.md` - Formatos y ejemplos reales
  - Estructura RPPScraper validada
  - Estructura PeruRailScraper validada
  - Ejemplos completos con datos reales
  - Estadísticas de extracción
  - Casos de uso turísticos
  - Mapeo: extracción → filtrado → alerta

- `VALIDACION_SPRINT2.md` - Reporte de validación
  - Datos integrados
  - Cambios realizados
  - Próximos pasos
  - Checklist final

- `SPRINT_REPORT_2.md` - Reporte formal de cierre
  - Resumen ejecutivo con KPIs
  - Tareas completadas (4/4)
  - Entregables técnicos
  - Datos reales validados
  - Arquitectura implementada
  - Métricas del sprint
  - Decisiones técnicas
  - Timeline

#### Infraestructura
- `requirements.txt` - Dependencias del proyecto
  - beautifulsoup4 - Parsing HTML
  - requests - HTTP client
  - selenium - Browser automation (futuro)
  - python-dotenv - Gestión de .env
  - openai - Integración con API (futuro)
  - pytest - Testing framework
  - black, flake8, pylint - Code quality

- `.gitignore` - Archivo de exclusiones
  - Python: `__pycache__/`, `*.pyc`, venv/
  - IDE: `.vscode/`, `.idea/`
  - Ambiente: `.env`, logs/
  - Data: datos locales, DBs

- `.env.example` - Plantilla de variables
  - API keys (OpenAI, Gemini, WhatsApp, Email)
  - URLs de fuentes
  - Configuración de BD
  - Settings de proyecto

#### Datos de Ejemplo
- `data/raw/alertas_rpp_20260424_1922.json` - 15 noticias RPP
- `data/raw/alertas_elcomercio_20260424_1922.json` - 10+ noticias El Comercio
- `data/raw/horarios_perurail_20260424_1922.json` - 60+ horarios PeruRail
- `data/raw/datos_cusco_relevantes_20260424_1922.json` - 60+ datos procesados

### Changed

Ningún cambio retroactivo (versión inicial).

### Deprecated

No hay funcionalidades deprecadas.

### Removed

No hay funcionalidades removidas.

### Fixed

No hay fixes en versión inicial.

### Security

- Plantilla `.env.example` sin valores sensibles
- `.gitignore` protege `.env` real
- No hay credenciales en repositorio

---

## [Unreleased]

### Planeado para Sprint 3: Motor de Razonamiento

#### Features
- [ ] Integración con OpenAI API
- [ ] Integración con Google Gemini API
- [ ] Clasificador de urgencia (URGENTE, ALTA, NORMAL)
- [ ] Filtro de relevancia turística
- [ ] Deduplicación temporal de alertas
- [ ] Scoring automático de impacto

#### Infrastructure
- [ ] ElasticsearchIntegration para logging
- [ ] CloudWatch para monitoring
- [ ] RateLimiter para APIs externas
- [ ] Cache de resultados

#### Documentación
- [ ] ARQUITECTURA_SPRINT3.md
- [ ] EJEMPLOS_CLASIFICACION.md
- [ ] API_REFERENCE.md

---

## Guía de Versionado

Este proyecto usa `MAJOR.MINOR.PATCH-PHASE` format:

- **MAJOR:** Cambios incompatibles
- **MINOR:** Nuevas features compatibles
- **PATCH:** Fixes de bugs
- **PHASE:** Sprint actual (sprint2, sprint3, etc)

Ejemplos:
- `0.1.0-sprint2` - Versión de desarrollo Sprint 2
- `1.0.0` - Release a producción
- `1.1.0` - Nuevo feature compatible
- `1.0.1` - Bug fix

---

## Cómo Contribuir

1. Crear rama desde `main`: `git checkout -b feature/descripcion`
2. Hacer cambios y commits semánticos
3. Abrir Pull Request con descripción
4. Actualizar este CHANGELOG en sección `[Unreleased]`

### Formato de Commits

```
feat: Descripción de feature
fix: Descripción de fix
docs: Actualización de documentación
refactor: Refactorización de código
test: Agregar tests
chore: Tareas de mantenimiento
```

---

## Información de Release

**Sprint 2 Release Date:** 24 de Abril de 2026  
**Sprint 2 Release Manager:** Honorio Morales Ttito  
**Sprint 2 QA:** Sebastian Zavaleta Luna  

---

## Referencias

- [GitHub Repository](https://github.com/Honorio-Morales/cusconodes)
- [Project Documentation](./docs)
- [Issue Tracker](https://github.com/Honorio-Morales/cusconodes/issues)

