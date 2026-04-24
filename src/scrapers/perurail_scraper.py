"""
PeruRail Scraper - Extractor de comunicados y horarios de PeruRail
"""

from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class PeruRailScraper(BaseScraper):
    """
    Scraper especializado para comunicados y horarios de PeruRail.
    Extrae información sobre cierres, cambios de horarios y avisos.
    """

    def __init__(self):
        """Inicializa el scraper de PeruRail"""
        super().__init__(
            name="PeruRail Horarios",
            url="https://www.perurail.com"
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Realiza el scraping de horarios y comunicados de PeruRail.

        Returns:
            List[Dict[str, Any]]: Lista de horarios extraídos
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Buscar filas de horarios en tablas
            schedules = soup.find_all('tr', class_='schedule-row')
            
            parsed_schedules = [self.parse_article(schedule) for schedule in schedules]
            parsed_schedules = self.add_metadata(parsed_schedules)
            
            self.logger.info(f"Se extrajeron {len(parsed_schedules)} horarios de PeruRail")
            return parsed_schedules
            
        except requests.RequestException as e:
            self.logger.error(f"Error al conectar con PeruRail: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error en scraping de PeruRail: {e}")
            return []

    def parse_article(self, article: Any) -> Dict[str, Any]:
        """
        Parsea un horario individual de PeruRail.
        Estructura: {servicio, salida, llegada, ruta, fecha_scrape}

        Args:
            article: Elemento del HTML (fila de tabla)

        Returns:
            Dict[str, Any]: Horario estructurado
        """
        try:
            cells = article.find_all('td')
            
            servicio = cells[0].text.strip() if len(cells) > 0 else ""
            salida = cells[1].text.strip() if len(cells) > 1 else ""
            llegada = cells[2].text.strip() if len(cells) > 2 else ""
            ruta = cells[3].text.strip() if len(cells) > 3 else ""
            
            return {
                'servicio': servicio,
                'salida': salida,
                'llegada': llegada,
                'ruta': ruta,
                'fecha_scrape': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            self.logger.error(f"Error parseando horario: {e}")
            return {}

