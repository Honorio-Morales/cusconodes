```
xt
```

```
Actúa como un Ingeniero de Machine Learning Senior. Vamos a implementar el
"Motor de Razonamiento Local" para el Sprint 3 de CuscoNodes.
```

```
Necesito crear el archivo `src/reasoning_agent.py`. Este componente debe cumplir
con los siguientes requisitos estrictos:
```

```
1. Contener un dataset de entrenamiento interno pequeño (mínimo 18 ejemplos
significativos de la realidad de Cusco: bloqueos en Ollantaytambo, huelgas de
transportistas, lluvias en Machu Picchu, noticias irrelevantes de fútbol o
política nacional).
```

```
2. Entrenar de manera síncrona y local (al instanciar la clase) un clasificador
utilizando scikit-learn (usa un pipeline clásico `CountVectorizer` +
`TfidfTransformer` + `MultinomialNB` o `LogisticRegression`) para predecir la
'urgencia': [CRÍTICA, INFORMATIVA, IRRELEVANTE].
```

```
3. Implementar un método heurístico o basado en reglas de coincidencia de
palabras clave para extraer:
```

- ``ubicaciones_detectadas`: (ej. "Machu Picchu", "Ollantaytambo",` 

```
"Sacsayhuamán", "Poroy", "Urubamba").
```

- ``tipo_evento`: [bloqueo_vias, clima, huelga, operativo].` 

```
4. Generar una recomendación textual automática basada en el tipo de evento y la
urgencia (ej. "Se sugiere a las agencias suspender traslados hacia el Valle
Sagrado").
```

```
Devuélveme el código limpio, documentado en español y optimizado para ejecutarse
localmente con un consumo de RAM menor a 500 MB.
```

```
🔄 Fase 2: El Pipeline de Integración de Datos
Necesitamos un script que tome los JSON en bruto producidos por los scrapers del
Sprint 2, los pase por el nuevo src/reasoning_agent.py y guarde el resultado
enriquecido.
```

```
🔄 Prompt 2: Creación del Script Demo del Pipeline (sprint3_reasoning_demo.py)
Instrucciones: Pega este prompt para unificar la percepción (Sprint 2) con el
razonamiento (Sprint 3).
```

## `Plaintext` 

```
Necesito crear un script en la raíz del proyecto llamado
`sprint3_reasoning_demo.py`.
```

```
Este script debe simular la ejecución completa del pipeline actual:
```

```
1. Debe leer el archivo JSON más reciente generado por los scrapers en el
directorio `data/processed/` (o generar un diccionario simulado de alertas
reales de Cusco si el directorio está vacío).
```

`2. Debe instanciar la clase del Motor de Razonamiento creada en` 

```
`src/reasoning_agent.py`.
```

```
3. Debe procesar cada alerta/noticia y generar un nuevo formato estructurado que
incluya:
```

- ``alerta_id` (Generar un UUIDv4 automáticamente)` 

- ``fuente_origen`` 

- ``texto_crudo`` 

- ``urgencia` (Calculada por el modelo ML)` 

- ``tipo_evento`` 

- ``ubicaciones_detectadas`` 

- ``recomendaciones_locales`` 

`4. Debe guardar el resultado final en un archivo llamado` 

```
`data/processed/alertas_clasificadas_demo_final.json`.
Asegúrate de agregar prints en la consola detallados con colores o emoticonos
para que el Profesor vea el flujo en la terminal (" [Procesando]...", " [ML
Clasificación: CRÍTICA]...").
```

💻 `Fase 3: EL PRODUCTO VISUAL (Servidor y Dashboard Web) Esta es la parte más importante para el Patrocinador Israel Rondán y el Profesor Hugo Espetia. Vamos a construir una API en Python y una interfaz web moderna en HTML/JS para que interactúen con la IA.` 

- `🔄 Prompt 3: Creación del Servidor Backend (web_server.py) Plaintext` 

```
Crea un servidor web en la raíz del proyecto llamado `web_server.py` utilizando
Flask.
```

```
Debe proveer dos endpoints clave:
```

```
1. `GET /api/alerts`: Debe leer el archivo
```

```
`data/processed/alertas_clasificadas_demo_final.json` y retornar los datos en
formato JSON. Si el archivo no existe, debe retornar un array vacío con estado
200.
```

```
2. `POST /api/process`: Debe disparar la lógica de `sprint3_reasoning_demo.py`
de forma síncrona (re-ejecutar el scraping y el procesamiento del modelo de IA)
y devolver el JSON actualizado.
```

```
Asegúrate de habilitar CORS (`flask_cors`) para que cualquier archivo HTML local
pueda consumir la API sin restricciones de seguridad del navegador.
🔄 Prompt 4: El Dashboard Interactivo (web/index.html)
Plaintext
Crea un archivo de interfaz web en `web/index.html`. Este será el producto
principal que mostraremos al patrocinador y al profesor en la Review del Sprint
3.
```

```
Requisitos de Diseño e Interacción:
```

```
1. Estructura visual moderna: Usa Tailwind CSS mediante CDN con una paleta de
colores oscura, profesional y tecnológica (fondos tipo slate-900, detalles en
azul índigo y verde esmeralda).
```

```
2. Encabezado institucional: Debe incluir el título del proyecto "CuscoNodes -
Panel de Control Agéntico (Sprint 3)", el nombre del Grupo "HABA" y una mención
al Patrocinador "Israel Rondán".
```

```
3. Botón de Acción Principal: Un botón llamativo que diga " Ejecutar Pipeline de
Razonamiento Local (IA)". Al presionarlo, debe hacer un POST a `/api/process`
mostrando un loader animado mientras la IA clasifica.
```

```
4. Sección "Flujo de Procesamiento en Tiempo Real" (Pipeline visual):
```

```
   - Tarjeta Izquierda: "Módulo de Percepción (Sprint 2)" -> Muestra el texto
original en bruto extraído de las fuentes web.
```

```
   - Tarjeta Central: "Motor de Razonamiento (Sprint 3)" -> Muestra una insignia
animada con el nivel de Urgencia (Rojo para CRÍTICA, Amarillo para INFORMATIVA,
Gris para IRRELEVANTE) calculada por el algoritmo de Machine Learning.
```

```
   - Tarjeta Derecha: "Entidades y Acciones" -> Muestra en formato de etiquetas
visuales atractivas las ubicaciones detectadas (ej. Ollantaytambo) y el cuadro
de "Recomendación para la Agencia de Viajes".
```

```
5. Goma de código limpia: Usa Vanilla JavaScript nativo (`fetch`) para
conectarte al backend, limpiar contenedores y renderizar las tarjetas de forma
dinámica.
```

```
🔄 Fase 4: Protocolo de Ejecución y Demostración en Vivo
Una vez que la IA haya generado todos los archivos anteriores, los pasos para
que tú u otra persona ejecuten la demo desde cero son:
```

```
Iniciar el Servidor Backend:
```

```
Bash
```

```
python web_server.py
(El servidor se quedará escuchando en http://127.0.0.1:5000)
```

```
Ejecutar el pipeline inicial para generar los datos:
Abre otra terminal y ejecuta:
```

```
Bash
python sprint3_reasoning_demo.py
Ver el Producto:
```

```
Abre el archivo web/index.html directamente en tu navegador web Chrome o Edge
(puedes arrastrar el archivo o usar la extensión Live Server de tu editor).
```

```
🔄 Estrategia para la presentación ante el jurado:
Paso 1: Muestra la carpeta data/ vacía o solo con los datos brutos del Sprint 2.
```

```
Paso 2: Abre el navegador, muestra la web interactiva limpia y presiona el botón
de "Ejecutar Pipeline".
```

```
Paso 3: Muestra cómo instantáneamente la interfaz web se puebla con las alertas
reales clasificadas por el modelo local (demostrando cumplimiento de
restricciones de hardware) y cómo extrae los sitios arqueológicos
automáticamente, dándole el valor directo de negocio que el patrocinador Israel
Rondán solicitó.
```

```
***
```

```
Con esta guía estructurada en Markdown, tu herramienta OpenCode entenderá
perfectamente la
```

