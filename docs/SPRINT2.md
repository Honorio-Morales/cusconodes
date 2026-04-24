# Sprint 2: Módulo de Percepción - Checklist

## Tareas Completadas ✅

### Estructura del Proyecto
- [x] Crear estructura de carpetas
  - [x] `/src/scrapers/` - Módulos de extracción
  - [x] `/src/config/` - Configuración
  - [x] `/data/raw/` - Almacenamiento de datos crudos
  - [x] `/data/processed/` - Datos procesados (futuro)
  - [x] `/tests/` - Suite de pruebas
  - [x] `/docs/` - Documentación

### Configuración del Entorno Python
- [x] Crear `requirements.txt` con dependencias
- [x] Crear `.env.example` con variables de entorno
- [x] Crear `.gitignore` para Git
- [x] Crear `README.md` con instrucciones

### Base de Código
- [x] `BaseScraper` - Clase abstracta base
- [x] `RPPScraper` - Scraper para RPP Noticias Cusco
- [x] `PeruRailScraper` - Scraper para PeruRail
- [x] `Settings` - Gestión de configuración centralizada
- [x] `main.py` - Orquestador principal

### Testing
- [x] Suite básica de pruebas pytest
- [x] Tests de inicialización de scrapers

### Documentación
- [x] README.md con instrucciones de instalación
- [x] ARCHITECTURE.md con diagrama del sistema

---

## Tareas Pendientes ⏳

### Durante Sprint 2 (Semana 2)
- [ ] Refinar selectores CSS/XPath para RPP Noticias
- [ ] Refinar selectores CSS/XPath para PeruRail
- [ ] Ejecutar y validar scrapers en entorno real
- [ ] Agregar manejo de excepciones más robusto
- [ ] Agregar retry logic para conexiones fallidas

### Testing Ampliado
- [ ] Tests de parseo de artículos
- [ ] Tests de guardado a JSON
- [ ] Tests de manejo de errores
- [ ] Tests de metadata

### Documentación Adicional
- [ ] Guía de desarrollo para nuevos scrapers
- [ ] Troubleshooting de errores comunes

---

## Cómo Usar Esta Estructura

### 1. Clonar y Configurar
```bash
git clone https://github.com/Honorio-Morales/cusconodes.git
cd cusconodes
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configurar Variables de Entorno
```bash
# Editar .env con tus valores reales:
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
# ... etc
```

### 3. Ejecutar Scrapers
```bash
python -m src.main
```

### 4. Correr Tests
```bash
pytest tests/
pytest --cov=src tests/  # Con coverage
```

---

## Notas Técnicas

- **Dependencias clave:** beautifulsoup4, requests, selenium
- **Patrón de diseño:** Abstract Base Class (ABC) para extensibilidad
- **Almacenamiento:** JSON local (escalable a DB en Sprint 5)
- **Logging:** Centralizado con módulo `logging` estándar

---

## Contacto & Soporte

**Project Manager:** Honorio Morales Ttito  
**Patrocinador:** Israel Rondán (PDS Viajes)

