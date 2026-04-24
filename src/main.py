"""
Main - Orquestador principal del pipeline de CuscoNodes
"""

import logging
from src.config import Settings
from src.scrapers import RPPScraper, PeruRailScraper

# Configurar logging
Settings.configure_logging()
logger = logging.getLogger(__name__)


def main():
    """
    Función principal que orquesta el pipeline del Sprint 2.
    """
    logger.info("="*50)
    logger.info("Iniciando CuscoNodes - Sprint 2: Módulo de Percepción")
    logger.info("="*50)

    # Crear instancias de scrapers
    rpp_scraper = RPPScraper()
    perurail_scraper = PeruRailScraper()

    logger.info("Iniciando extracción de datos...")

    # Ejecutar scrapers
    logger.info("Scrapeando RPP Noticias Cusco...")
    rpp_articles = rpp_scraper.scrape()
    if rpp_articles:
        rpp_scraper.save_to_json(rpp_articles, f"{Settings.RAW_DATA_PATH}/rpp_noticias.json")

    logger.info("Scrapeando comunicados de PeruRail...")
    perurail_articles = perurail_scraper.scrape()
    if perurail_articles:
        perurail_scraper.save_to_json(perurail_articles, f"{Settings.RAW_DATA_PATH}/perurail_comunicados.json")

    logger.info("="*50)
    logger.info(f"Extracción completada:")
    logger.info(f"  - RPP: {len(rpp_articles)} artículos")
    logger.info(f"  - PeruRail: {len(perurail_articles)} comunicados")
    logger.info("="*50)


if __name__ == "__main__":
    main()

