# CELDA 2 - Código del Scraper para Cusco (Alertas + Horarios)

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

# Headers para simular un navegador real
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

# Palabras clave para detectar alertas de huelgas y bloqueos
KEYWORDS = ["huelga", "bloqueo", "paro", "protesta", "manifestacion",
            "corte", "vía cortada", "carretera cortada", "cusco"]

def contains_alert_keywords(text):
    """Verifica si el texto contiene palabras clave de alerta"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

# ====================== FUNCIONES DE SCRAPING ======================

def scrape_perurail_schedules():
    """Scraping de horarios de PeruRail"""
    url = "https://www.perurail.com/train-schedules-and-frequencies/"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        tables = soup.find_all('table')
        data = []

        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Saltar encabezado
                cols = row.find_all('td')
                if len(cols) >= 3:
                    data.append({
                        "servicio": cols[0].get_text(strip=True),
                        "salida": cols[1].get_text(strip=True),
                        "llegada": cols[2].get_text(strip=True),
                        "ruta": cols[3].get_text(strip=True) if len(cols) > 3 else "Cusco - Machu Picchu",
                        "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

        print(f"✅ PeruRail → {len(data)} horarios encontrados")
        return data
    except Exception as e:
        print(f"❌ Error en PeruRail: {e}")
        return []

def scrape_incarail_schedules():
    """Scraping de horarios de IncaRail"""
    url = "https://incarail.com/en/trains/train-schedules"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar elementos que puedan contener horarios
        items = soup.find_all(['div', 'tr', 'li'], class_=lambda x: x and any(word in str(x).lower() for word in ['schedule', 'train', 'time']))

        data = []
        for item in items:
            text = item.get_text(strip=True)
            if any(word in text.lower() for word in ['train', 'horario', 'departure']):
                data.append({
                    "descripcion": text[:200],  # Limitar longitud
                    "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        print(f"✅ IncaRail → {len(data)} registros encontrados")
        return data
    except Exception as e:
        print(f"❌ Error en IncaRail: {e}")
        return []

def scrape_alerts_rpp():
    """Scraping de ALERTAS en RPP Cusco"""
    url = "https://rpp.pe/peru/cusco"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.select('h2 a, h3 a, article h2 a, article h3 a')

        data = []
        for a in articles:
            title = a.get_text(strip=True)
            link = a.get('href')
            if link and not link.startswith('http'):
                link = "https://rpp.pe" + link

            if contains_alert_keywords(title):
                data.append({
                    "titulo": title,
                    "enlace": link,
                    "fuente": "RPP Cusco",
                    "tipo": "ALERTA",
                    "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        print(f"✅ RPP Alertas → {len(data)} alertas encontradas")
        return data
    except Exception as e:
        print(f"❌ Error en RPP Alertas: {e}")
        return []

def scrape_alerts_elcomercio():
    """Scraping de ALERTAS en El Comercio Cusco"""
    url = "https://elcomercio.pe/peru/cusco/"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.select('h2 a, h3 a, article h2, article h3')

        data = []
        for tag in articles:
            title = tag.get_text(strip=True)
            link = tag.get('href') if tag.name == 'a' else tag.find('a')['href'] if tag.find('a') else ''

            if link and not link.startswith('http'):
                link = "https://elcomercio.pe" + link if link.startswith('/') else link

            if contains_alert_keywords(title):
                data.append({
                    "titulo": title,
                    "enlace": link,
                    "fuente": "El Comercio Cusco",
                    "tipo": "ALERTA",
                    "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        print(f"✅ El Comercio Alertas → {len(data)} alertas encontradas")
        return data
    except Exception as e:
        print(f"❌ Error en El Comercio Alertas: {e}")
        return []

# ====================== EJECUCIÓN PRINCIPAL ======================

print("🚀 Iniciando scraping para proyecto Cusco...\n")

timestamp = datetime.now().strftime("%Y%m%d_%H%M")

# Scraping de horarios
data_perurail = scrape_perurail_schedules()
data_incarail = scrape_incarail_schedules()

# Scraping de alertas (solo huelgas y bloqueos)
data_alertas_rpp = scrape_alerts_rpp()
data_alertas_elcomercio = scrape_alerts_elcomercio()

# Guardar cada uno en su propio JSON
files_created = []

if data_perurail:
    filename = f"horarios_perurail_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_perurail, f, ensure_ascii=False, indent=2)
    files_created.append(filename)

if data_incarail:
    filename = f"horarios_incarail_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_incarail, f, ensure_ascii=False, indent=2)
    files_created.append(filename)

if data_alertas_rpp:
    filename = f"alertas_rpp_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_alertas_rpp, f, ensure_ascii=False, indent=2)
    files_created.append(filename)

if data_alertas_elcomercio:
    filename = f"alertas_elcomercio_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_alertas_elcomercio, f, ensure_ascii=False, indent=2)
    files_created.append(filename)

print("\n" + "="*60)
print("🎉 ¡SCRAPING FINALIZADO!")
print("="*60)
for file in files_created:
    print(f"📄 Archivo generado: {file}")

"""### Nota sobre Facebook

El scraping de Facebook es significativamente más complejo que el de sitios web estáticos o semi-estáticos. Esto se debe a varias razones:

1.  **Contenido Dinámico (JavaScript)**: Gran parte del contenido de Facebook se carga dinámicamente usando JavaScript, lo que Beautiful Soup (que solo analiza el HTML inicial) no puede procesar. Se requerirían herramientas como Selenium para simular un navegador.
2.  **Autenticación**: Para acceder a la mayoría de los perfiles y resultados de búsqueda, se necesita iniciar sesión, lo que complica el proceso de scraping.
3.  **Términos de Servicio**: El scraping de Facebook va en contra de sus términos de servicio, y la plataforma tiene mecanismos robustos para detectar y bloquear bots, lo que puede resultar en suspensiones de IP o cuentas.
4.  **Estructura Cambiante**: La estructura HTML de Facebook cambia con frecuencia, lo que hace que los selectores de Beautiful Soup sean muy inestables y propensos a romperse.

Por estas razones, no es factible realizar un scraping confiable y sostenible de los enlaces de Facebook proporcionados con las herramientas actuales de este notebook. Se recomienda buscar alternativas como la API oficial de Facebook (si está disponible para el tipo de datos deseado y si se tienen las credenciales adecuadas) o considerar que la información de Facebook es de acceso manual.
"""

# ====================== FUNCIONES DE SCRAPING (Adicional) ======================

def scrape_alerts_diariodelcusco():
    """Scraping de ALERTAS en Diario del Cusco"""
    url = "https://diariodelcusco.pe"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Selectores para títulos y enlaces en Diario del Cusco
        # Se buscan elementos 'h2' y 'h3' dentro de artículos o que tengan un enlace directo.
        articles = soup.select('article h2 a, article h3 a, .td-module-thumb a, .td-related-title a')

        data = []
        for a in articles:
            title = a.get('title') or a.get_text(strip=True)
            link = a.get('href')

            if link and not link.startswith('http'):
                link = "https://diariodelcusco.pe" + link

            if contains_alert_keywords(title):
                data.append({
                    "titulo": title,
                    "enlace": link,
                    "fuente": "Diario del Cusco",
                    "tipo": "ALERTA",
                    "fecha_scrape": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        print(f"✅ Diario del Cusco Alertas → {len(data)} alertas encontradas")
        return data
    except Exception as e:
        print(f"❌ Error en Diario del Cusco Alertas: {e}")
        return []

# ====================== ACTUALIZACIÓN DE EJECUCIÓN PRINCIPAL ======================

# Añadir el nuevo scraper a la ejecución principal
data_alertas_diariodelcusco = scrape_alerts_diariodelcusco()

# Guardar el nuevo JSON
if data_alertas_diariodelcusco:
    filename = f"noticiaslocal_{timestamp}.json" # Changed filename here
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_alertas_diariodelcusco, f, ensure_ascii=False, indent=2)
    files_created.append(filename)

print("\n" + "="*60)
print("🎉 ¡SCRAPING FINALIZADO!")
print("="*60)
for file in files_created:
    print(f"📄 Archivo generado: {file}")

# CELDA 3 - Ver archivos JSON generados en Colab
import os
print("Archivos generados en esta carpeta:")
for file in os.listdir():
    if file.endswith(".json"):
        print("   →", file)

# CELDA 3 - CARGAR + ESTANDARIZAR todos los JSON a un formato único (Recomendado)

import pandas as pd
import json
import glob
from datetime import datetime

# Buscar todos los archivos JSON generados por el scraping
json_files = glob.glob("*.json")
print(f"📁 Archivos JSON encontrados: {len(json_files)}\n")

all_records = []

for file in json_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            # Estandarización: todas las fuentes tendrán las mismas columnas
            record = {
                "id": len(all_records) + 1,
                "tipo": "horario" if any(x in file.lower() for x in ["perurail", "incarail"]) else "alerta",
                "titulo_descripcion": item.get("titulo") or
                                     item.get("servicio") or
                                     item.get("descripcion") or
                                     item.get("tren") or
                                     str(item.get("horarios", "")),
                "detalles": str(item),                    # Guarda toda la info original aquí
                "fuente": item.get("fuente", file.replace(".json", "")),
                "enlace": item.get("enlace", ""),
                "fecha_scrape": item.get("fecha_scrape", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "archivo_origen": file
            }
            all_records.append(record)

        print(f"✅ Procesado: {file} → {len(data)} registros")

    except Exception as e:
        print(f"❌ Error al procesar {file}: {e}")

# Crear DataFrame estandarizado
df = pd.DataFrame(all_records)

print(f"\n📊 DataFrame estandarizado creado con éxito: {len(df)} filas")
print("Columnas finales:", df.columns.tolist())
df.head()

# CELDA 4 - Limpieza + Normalización + Clasificación por urgencia

# 1. Eliminar duplicados
df = df.drop_duplicates(subset=['titulo_descripcion'], keep='last')
print(f"✅ Duplicados eliminados → {len(df)} registros restantes")

# 2. Normalizar texto (minúsculas y limpiar)
def normalize_text(text):
    if pd.isna(text) or not text:
        return ""
    return str(text).strip().lower()

df['titulo_descripcion'] = df['titulo_descripcion'].apply(normalize_text)

# 3. Convertir fecha
df['fecha_scrape'] = pd.to_datetime(df['fecha_scrape'], errors='coerce')

# 4. Clasificación de urgencia
KEYWORDS_URGENTES = ["huelga", "bloqueo", "paro", "protesta", "manifestacion",
                     "corte", "vía cortada", "carretera cortada", "lluvia",
                     "inundacion", "derrumbe"]

def clasificar_urgencia(texto):
    if not texto:
        return "BAJA"
    texto = texto.lower()
    if any(kw in texto for kw in KEYWORDS_URGENTES):
        return "URGENTE"
    elif any(word in texto for word in ["mañana", "hoy", "tarde", "inmediato"]):
        return "ALTA"
    else:
        return "NORMAL"

df['urgencia'] = df['titulo_descripcion'].apply(clasificar_urgencia)

# Filtrar solo lo más relevante
df_relevante = df[
    (df['urgencia'].isin(['URGENTE', 'ALTA'])) |
    (df['tipo'] == 'horario')
]

print(f"\n📈 Resumen:")
print(f"   Total registros después de limpieza : {len(df)}")
print(f"   Registros relevantes                 : {len(df_relevante)}")
print(f"   Alertas URGENTES                     : {(df_relevante['urgencia'] == 'URGENTE').sum()}")

# Mostrar distribución
print("\nDistribución por urgencia:")
print(df_relevante['urgencia'].value_counts())

df_relevante.head()

# CELDA 5 - Guardar resultados limpios

# ====================== GUARDAR PARA EL DASHBOARD ======================
# Guardamos la versión fija para el frontend
df_relevante.to_json("../ultimas_noticias.json", orient='records', force_ascii=False, indent=2)

# Guardamos el histórico con timestamp por seguridad
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
df_relevante.to_json(f"../data/cusco_backup_{timestamp}.json", orient='records', force_ascii=False, indent=2)

print("✅ Sincronización completa: 'latest_news.json' ha sido actualizado.")

