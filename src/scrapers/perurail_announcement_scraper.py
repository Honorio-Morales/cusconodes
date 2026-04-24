"""
PeruRail Announcement Scraper - Detecta suspensiones y avisos de servicio
"""

from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class PeruRailAnnouncementScraper(BaseScraper):
    """
    Scraper especializado para avisos y suspensiones de PeruRail.
    Detecta: paros, cierres de vías, cambios operacionales.
    
    Palabras clave de suspensión:
    - "suspensión", "cancelado", "cancelada"
    - "parado", "paro", "huelga"
    - "cierre", "cerrado", "clausurado"
    - "mantenimiento", "reparación"
    """

    def __init__(self):
        """Inicializa el scraper de avisos de PeruRail"""
        super().__init__(
            name="PeruRail Avisos Servicio",
            url="https://www.perurail.com/es/noticias"
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.suspension_keywords = [
            'suspensión', 'suspendido', 'suspendida',
            'cancelado', 'cancelada', 'cancelados',
            'parado', 'paro', 'huelga',
            'cierre', 'cerrado', 'clausurado',
            'mantenimiento', 'reparación',
            'servicio no disponible', 'fuera de servicio'
        ]

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Realiza el scraping de avisos de suspensión en PeruRail.

        Returns:
            List[Dict[str, Any]]: Lista de avisos de suspensión
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Buscar secciones de avisos/noticias
            announcements = soup.find_all('div', class_=['announcement', 'alert', 'notice'])
            
            parsed_announcements = [self.parse_article(ann) for ann in announcements]
            
            # Filtrar solo suspensiones
            suspensions = [
                ann for ann in parsed_announcements 
                if ann and self._is_suspension(ann)
            ]
            
            suspensions = self.add_metadata(suspensions)
            
            self.logger.info(f"Se encontraron {len(suspensions)} suspensiones en PeruRail")
            return suspensions
            
        except requests.RequestException as e:
            self.logger.error(f"Error al conectar con PeruRail: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error en scraping de avisos PeruRail: {e}")
            return []

    def parse_article(self, article: Any) -> Dict[str, Any]:
        """
        Parsea un aviso individual de PeruRail.
        
        Estructura:
        {
            'titulo': str,
            'descripcion': str,
            'fecha_publicacion': str,
            'ruta_afectada': str,
            'tipo_suspension': str,
            'urgencia': str
        }

        Args:
            article: Elemento del HTML

        Returns:
            Dict[str, Any]: Aviso estructurado
        """
        try:
            # Extraer título
            title_elem = article.find(['h2', 'h3', 'h4'])
            titulo = title_elem.text.strip() if title_elem else "Sin título"
            
            # Extraer descripción
            desc_elem = article.find('p')
            descripcion = desc_elem.text.strip() if desc_elem else ""
            
            # Extraer fecha
            date_elem = article.find(['span', 'time'], class_=['date', 'published'])
            fecha_publicacion = date_elem.text.strip() if date_elem else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Determinar ruta afectada
            ruta_afectada = self._extract_route(titulo + " " + descripcion)
            
            # Determinar tipo de suspensión
            tipo_suspension = self._categorize_suspension(titulo + " " + descripcion)
            
            # Determinar urgencia basada en palabras clave
            urgencia = self._calculate_urgency(titulo + " " + descripcion)
            
            return {
                'titulo': titulo,
                'descripcion': descripcion,
                'fecha_publicacion': fecha_publicacion,
                'ruta_afectada': ruta_afectada,
                'tipo_suspension': tipo_suspension,
                'urgencia': urgencia,
                'fuente': self.name,
                'tipo': 'SUSPENSION',
                'fecha_scrape': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            self.logger.error(f"Error parseando aviso: {e}")
            return {}

    def _is_suspension(self, announcement: Dict[str, Any]) -> bool:
        """
        Verifica si un anuncio es una suspensión de servicio.
        
        Args:
            announcement: Diccionario del anuncio
            
        Returns:
            bool: True si es una suspensión
        """
        text = (announcement.get('titulo', '') + " " + 
                announcement.get('descripcion', '')).lower()
        
        return any(keyword in text for keyword in self.suspension_keywords)

    def _extract_route(self, text: str) -> str:
        """
        Extrae la ruta afectada del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            str: Ruta identificada
        """
        routes = [
            'Cusco-Machu Picchu',
            'Wanchaq',
            'Ollantaytambo',
            'Machu Picchu Pueblo',
            'Hidroeléctrica',
            'Poroy',
            'San Pedro'
        ]
        
        for route in routes:
            if route.lower() in text.lower():
                return route
        
        return "No especificada"

    def _categorize_suspension(self, text: str) -> str:
        """
        Categoriza el tipo de suspensión.
        
        Args:
            text: Texto a analizar
            
        Returns:
            str: Tipo de suspensión
        """
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['paro', 'huelga', 'protesta']):
            return 'PARO_LABORAL'
        elif any(word in text_lower for word in ['mantenimiento', 'reparación', 'limpieza']):
            return 'MANTENIMIENTO'
        elif any(word in text_lower for word in ['lluvia', 'tormenta', 'nieve', 'clima']):
            return 'CONDICIONES_CLIMATICAS'
        elif any(word in text_lower for word in ['accidente', 'falla', 'derrame']):
            return 'EMERGENCIA'
        else:
            return 'OTRA'

    def _calculate_urgency(self, text: str) -> str:
        """
        Calcula el nivel de urgencia basado en palabras clave.
        
        Args:
            text: Texto a analizar
            
        Returns:
            str: Nivel de urgencia (URGENTE, ALTA, NORMAL)
        """
        text_lower = text.lower()
        
        urgent_words = ['urgente', 'inmediato', 'ahora', 'emergencia', 'crítico']
        high_words = ['hoy', 'esta semana', 'próximo', 'reparación', 'mantenimiento']
        
        if any(word in text_lower for word in urgent_words):
            return 'URGENTE'
        elif any(word in text_lower for word in high_words):
            return 'ALTA'
        else:
            return 'NORMAL'
