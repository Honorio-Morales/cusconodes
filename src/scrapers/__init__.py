"""
Módulo de Scrapers - Extracción de datos desde fuentes locales
"""

from .base_scraper import BaseScraper
from .rpp_scraper import RPPScraper
from .perurail_scraper import PeruRailScraper

__all__ = ["BaseScraper", "RPPScraper", "PeruRailScraper"]

