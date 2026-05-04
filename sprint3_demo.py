#!/usr/bin/env python3
"""
Sprint 3 Demo - Pipeline Completo: Percepción → Razonamiento → Almacenamiento

Demuestra el funcionamiento del sistema agéntico con 3 etapas:
1. Percepción: Scrapers extraen datos
2. Razonamiento: IA clasifica y decide
3. Almacenamiento: Guardado en JSON procesado
"""

import sys
import os
import logging
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.rpp_scraper import RPPScraper
from src.scrapers.perurail_scraper import PeruRailScraper
from src.scheduler import CuscoNodesScheduler


def demo_sprint3():
    """
    Ejecuta una demostración del pipeline completo de Sprint 3.
    """
    
    print("\n" + "="*70)
    print("🚀 CUSCONODES - SPRINT 3 DEMO")
    print("Sistema Agéntico: Percepción → Razonamiento → Acción")
    print("="*70 + "\n")
    
    try:
        # Inicializar componentes
        logger.info("📦 Inicializando componentes...")
        
        # Crear scheduler
        scheduler = CuscoNodesScheduler(data_path='./data')
        
        # Crear scrapers
        scrapers = [
            RPPScraper(),
            PeruRailScraper()
        ]
        
        logger.info(f"✅ {len(scrapers)} scrapers configurados\n")
        
        # Ejecutar pipeline completo
        logger.info("🔄 Ejecutando pipeline completo...")
        logger.info("-" * 70)
        
        result = scheduler.run_full_pipeline(scrapers)
        
        logger.info("-" * 70 + "\n")
        
        # Mostrar resultados
        print_results(result, scheduler)
        
        # Cargar y mostrar algunas alertas clasificadas
        if result.get('reasoning_applied'):
            print_classified_alerts(scheduler)
        
        print("\n" + "="*70)
        print("✅ DEMO COMPLETADA")
        print("="*70 + "\n")
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Error en demo: {e}", exc_info=True)
        return None


def print_results(result, scheduler):
    """Imprime resultados del pipeline."""
    
    print("\n📊 RESULTADOS DEL PIPELINE:")
    print("-" * 70)
    
    print(f"\nEtapa 1 - PERCEPCIÓN:")
    print(f"  ✅ Scrapers ejecutados: {len(result.get('scrapers_executed', []))}")
    print(f"  📊 Total alertas extraídas: {result.get('total_alerts_raw', 0)}")
    
    for scraper_result in result.get('scrapers_executed', []):
        status = "✅" if scraper_result.get('status') == 'success' else "❌"
        print(f"     {status} {scraper_result['name']}: {scraper_result.get('records', 0)} registros")
    
    print(f"\nEtapa 2 - RAZONAMIENTO:")
    if result.get('reasoning_applied'):
        print(f"  ✅ IA Aplicada (Transformers)")
        print(f"  📊 Alertas críticas detectadas: {result.get('total_alerts_critical', 0)}")
    else:
        print(f"  ⚠️  Modo legacy (filtrado simple)")
    
    print(f"\nEtapa 3 - ALMACENAMIENTO:")
    print(f"  📁 Archivos creados: {len(result.get('files_created', []))}")
    for file in result.get('files_created', [])[:3]:  # Mostrar primeros 3
        print(f"     📄 {os.path.basename(file)}")
    
    print(f"\nEstado final: {result.get('status', 'unknown').upper()}")


def print_classified_alerts(scheduler):
    """Imprime ejemplos de alertas clasificadas."""
    
    print("\n📋 EJEMPLOS DE ALERTAS CLASIFICADAS:")
    print("-" * 70)
    
    # Buscar último archivo de alertas clasificadas
    processed_path = os.path.join(scheduler.processed_path)
    
    if not os.path.exists(processed_path):
        logger.warning("No hay alertas clasificadas disponibles")
        return
    
    files = sorted([f for f in os.listdir(processed_path) if f.startswith('alertas_clasificadas_')])
    
    if not files:
        logger.warning("No hay archivos de alertas clasificadas")
        return
    
    latest_file = os.path.join(processed_path, files[-1])
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            alerts = json.load(f)
        
        # Mostrar solo CRÍTICAS
        critical_alerts = [a for a in alerts if a.get('clasificacion') == 'CRÍTICA']
        
        if not critical_alerts:
            print("\n✅ No hay alertas críticas en esta ejecución (buen signo)")
            return
        
        print(f"\n🚨 Alertas Críticas ({len(critical_alerts)}):\n")
        
        for alert in critical_alerts[:3]:  # Mostrar primeras 3
            print(f"  Título: {alert.get('titulo', '')[:60]}")
            print(f"  Fuente: {alert.get('fuente', '')}")
            print(f"  Clasificación: {alert.get('clasificacion', '')} (confianza: {alert.get('confianza', 0)}%)")
            print(f"  Ubicaciones: {', '.join(alert.get('ubicaciones', ['N/A']))}")
            print(f"  Recomendación: {alert.get('recomendacion', 'N/A')}")
            print()
    
    except Exception as e:
        logger.error(f"Error leyendo alertas clasificadas: {e}")


if __name__ == '__main__':
    demo_sprint3()
