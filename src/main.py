"""
Main - Orquestador principal del pipeline de CuscoNodes
"""

import logging
from src.config import Settings
from src.scrapers import (
    RPPScraper, 
    PeruRailScraper, 
    PeruRailAnnouncementScraper,
    AlertFilter
)
from src.scheduler import CuscoNodesScheduler

# Configurar logging
Settings.configure_logging()
logger = logging.getLogger(__name__)


def main():
    """
    Función principal que orquesta el pipeline completo del Sprint 2.
    
    Pipeline:
    1. Percepción: Ejecutar scrapers
    2. Filtrado: Identificar alertas críticas
    3. Almacenamiento: Guardar datos raw y procesados
    4. Resumen: Generar reporte de alertas
    """
    
    # Inicializar componentes
    logger.info("\n" + "="*70)
    logger.info("🚀 CUSCONODES - SISTEMA DE ALERTAS AGÉNTICO PARA TURISTAS")
    logger.info("Sprint 2: Módulo de Percepción")
    logger.info("="*70 + "\n")
    
    # Crear instancias de scrapers
    scrapers = [
        RPPScraper(),
        PeruRailScraper(),
        PeruRailAnnouncementScraper()
    ]
    
    # Crear filtrador de alertas
    alert_filter = AlertFilter(dedup_hours=6)
    
    # Crear scheduler
    scheduler = CuscoNodesScheduler(data_path=Settings.DATA_STORAGE_PATH)
    
    # Ejecutar pipeline completo
    logger.info("Iniciando pipeline completo...")
    result = scheduler.run_full_pipeline(scrapers, alert_filter)
    
    # Mostrar resultados
    logger.info("\n" + "="*70)
    logger.info("📊 RESULTADOS DEL PIPELINE")
    logger.info("="*70)
    logger.info(f"Status: {result['status'].upper()}")
    logger.info(f"Alertas extraídas: {result['total_alerts_raw']}")
    logger.info(f"Alertas críticas: {result['total_alerts_critical']}")
    logger.info(f"Archivos creados: {len(result['files_created'])}")
    logger.info("="*70 + "\n")
    
    # Mostrar alertas críticas
    if result['total_alerts_critical'] > 0:
        logger.info("⚠️  ALERTAS CRÍTICAS IDENTIFICADAS:")
        recent = scheduler.get_latest_critical_alerts(limit=5)
        for i, alert in enumerate(recent, 1):
            logger.info(f"\n{i}. {alert.get('titulo', 'N/A')}")
            logger.info(f"   Fuente: {alert.get('fuente', 'N/A')}")
            logger.info(f"   Urgencia: {alert.get('urgencia', 'N/A')}")
            logger.info(f"   Criticidad: {alert.get('criticidad', 'N/A'):.0f}/100")
    
    logger.info("\n✅ Pipeline completado\n")
    
    return result


if __name__ == "__main__":
    main()


