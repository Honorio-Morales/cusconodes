"""
CuscoNodes - Sistema de Inteligencia Artificial Agéntica
Módulo principal del proyecto
"""

__version__ = "0.1.0-sprint2"
__author__ = "Honorio Morales Ttito"
__project__ = "CuscoNodes"
__description__ = "Sistema de alertas inteligente para turistas en Cusco"

from .scheduler import CuscoNodesScheduler
from .scrapers import (
    BaseScraper,
    RPPScraper,
    PeruRailScraper,
    PeruRailAnnouncementScraper,
    AlertFilter
)
from .config import Settings

__all__ = [
    "CuscoNodesScheduler",
    "BaseScraper",
    "RPPScraper",
    "PeruRailScraper",
    "PeruRailAnnouncementScraper",
    "AlertFilter",
    "Settings"
]

