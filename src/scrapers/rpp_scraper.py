"""
RPP Scraper - Extractor de noticias de RPP Noticias Cusco
"""

from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class RPPScraper(BaseScraper):
    """
    Scraper especializado para RPP Noticias - Sección Cusco.
    Extrae noticias relevantes para turistas.
    """

    def __init__(self):
        """Inicializa el scraper de RPP"""
        super().__init__(
            name="RPP Noticias Cusco",
            url="https://rpp.pe/cusco"
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Realiza el scraping de RPP Noticias Cusco.

        Returns:
            List[Dict[str, Any]]: Lista de noticias extraídas
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article', class_='article')
            
            parsed_articles = [self.parse_article(article) for article in articles]
            parsed_articles = self.add_metadata(parsed_articles)
            
            self.logger.info(f"Se extrajeron {len(parsed_articles)} artículos de RPP")
            return parsed_articles
            
        except requests.RequestException as e:
            self.logger.error(f"Error al conectar con RPP: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error en scraping de RPP: {e}")
            return []

    def parse_article(self, article: Any) -> Dict[str, Any]:
        """
        Parsea un artículo individual de RPP.

        Args:
            article: Elemento del HTML

        Returns:
            Dict[str, Any]: Artículo estructurado
        """
        try:
            title_elem = article.find('h2')
            title = title_elem.text.strip() if title_elem else "Sin título"
            
            url_elem = article.find('a')
            url = url_elem['href'] if url_elem else ""
            
            description_elem = article.find('p', class_='description')
            description = description_elem.text.strip() if description_elem else ""
            
            return {
                'title': title,
                'description': description,
                'url': url,
                'source_name': self.name
            }
        except Exception as e:
            self.logger.error(f"Error parseando artículo: {e}")
            return {}

