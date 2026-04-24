"""
Test Scrapers - Suite de pruebas para los módulos de scraping
"""

import pytest
from src.scrapers import BaseScraper, RPPScraper, PeruRailScraper


class TestRPPScraper:
    """Tests para el scraper de RPP"""

    def test_rpp_initialization(self):
        """Verifica que RPPScraper se inicialice correctamente"""
        scraper = RPPScraper()
        assert scraper.name == "RPP Noticias Cusco"
        assert scraper.url == "https://rpp.pe/cusco"

    def test_rpp_scrape_returns_list(self):
        """Verifica que scrape retorna una lista"""
        scraper = RPPScraper()
        result = scraper.scrape()
        assert isinstance(result, list)


class TestPeruRailScraper:
    """Tests para el scraper de PeruRail"""

    def test_perurail_initialization(self):
        """Verifica que PeruRailScraper se inicialice correctamente"""
        scraper = PeruRailScraper()
        assert scraper.name == "PeruRail Comunicados"
        assert scraper.url == "https://www.perurail.com"

    def test_perurail_scrape_returns_list(self):
        """Verifica que scrape retorna una lista"""
        scraper = PeruRailScraper()
        result = scraper.scrape()
        assert isinstance(result, list)

