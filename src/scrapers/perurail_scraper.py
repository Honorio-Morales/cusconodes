"""
PeruRail Scraper - Extractor de comunicados de PeruRail
"""

from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class PeruRailScraper(BaseScraper):
    """
    Scraper especializado para comunicados de PeruRail.
    Extrae información sobre cierres, cambios de horarios y avisos.
    """

    def __init__(self):
        """Inicializa el scraper de PeruRail"""
        super().__init__(
            name="PeruRail Comunicados",
            url="https://www.perurail.com"
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Realiza el scraping de comunicados de PeruRail.

        Returns:
            List[Dict[str, Any]]: Lista de comunicados extraídos
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Buscar comunicados en la estructura específica de PeruRail
            announcements = soup.find_all('div', class_='announcement')
            
            parsed_announcements = [self.parse_article(ann) for ann in announcements]
            parsed_announcements = self.add_metadata(parsed_announcements)
            
            self.logger.info(f"Se extrajeron {len(parsed_announcements)} comunicados de PeruRail")
            return parsed_announcements
            
        except requests.RequestException as e:
            self.logger.error(f"Error al conectar con PeruRail: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error en scraping de PeruRail: {e}")
            return []

    def parse_article(self, article: Any) -> Dict[str, Any]:
        """
        Parsea un comunicado individual de PeruRail.

        Args:
            article: Elemento del HTML

        Returns:
            Dict[str, Any]: Comunicado estructurado
        """
        try:
            title_elem = article.find('h3')
            title = title_elem.text.strip() if title_elem else "Sin título"
            
            content_elem = article.find('p')
            content = content_elem.text.strip() if content_elem else ""
            
            date_elem = article.find('span', class_='date')
            date = date_elem.text.strip() if date_elem else ""
            
            return {
                'title': title,
                'content': content,
                'date': date,
                'source_name': self.name,
                'type': 'announcement'
            }
        except Exception as e:
            self.logger.error(f"Error parseando comunicado: {e}")
            return {}

