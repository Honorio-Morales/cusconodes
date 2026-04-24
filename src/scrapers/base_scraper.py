"""
Base Scraper - Clase base para todos los scrapers
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
import json
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Clase base para todos los scrapers del sistema.
    Define la interfaz común para la extracción de datos.
    """

    def __init__(self, name: str, url: str):
        """
        Inicializa el scraper base.

        Args:
            name (str): Nombre del scraper
            url (str): URL base para scraping
        """
        self.name = name
        self.url = url
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Método abstracto para realizar el scraping.

        Returns:
            List[Dict[str, Any]]: Lista de artículos extraídos
        """
        pass

    @abstractmethod
    def parse_article(self, article: Any) -> Dict[str, Any]:
        """
        Método abstracto para parsear un artículo individual.

        Args:
            article: Elemento del HTML a parsear

        Returns:
            Dict[str, Any]: Artículo estructurado
        """
        pass

    def save_to_json(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        Guarda los datos extraídos en un archivo JSON.

        Args:
            data (List[Dict[str, Any]]): Datos a guardar
            filename (str): Nombre del archivo
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Datos guardados en {filename}")
        except Exception as e:
            self.logger.error(f"Error al guardar datos: {e}")

    def add_metadata(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Añade metadatos a los artículos.
        Mantiene los campos existentes sin modificarlos.

        Args:
            articles (List[Dict[str, Any]]): Artículos a enriquecer

        Returns:
            List[Dict[str, Any]]: Artículos con metadatos
        """
        for article in articles:
            # Solo agregar metadatos si no existen
            if 'fuente' not in article:
                article['fuente'] = self.name
            if 'fecha_scrape' not in article:
                article['fecha_scrape'] = datetime.now().isoformat()
        return articles

