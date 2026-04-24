"""
Alert Filter - Sistema de filtrado de alertas críticas para turistas
"""

from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlertFilter:
    """
    Filtra alertas para identificar solo las críticas para turistas.
    
    Criterios de filtrado:
    1. Palabras clave de impacto turístico
    2. Ubicación: solo Cusco y zonas turísticas
    3. Urgencia: URGENTE o ALTA
    4. Deduplicación temporal: no repetir alertas recientes
    """

    # Palabras clave que indican impacto turístico
    TOURIST_IMPACT_KEYWORDS = [
        # Transporte
        'machu picchu', 'tren', 'ferrocarril', 'estación', 'transporte',
        'cusco', 'ollantaytambo', 'wanchaq', 'aguas calientes',
        
        # Atracciones
        'vinicunca', 'montaña de colores', 'ruinas', 'inca',
        'plaza de armas', 'sacsayhuamán', 'piscac',
        
        # Riesgos
        'cierres', 'suspensión', 'cierre de vías', 'deslizamiento',
        'lluvia', 'nieve', 'inundación', 'alud',
        'huelga', 'protesta', 'marcha',
        
        # Emergencias
        'accidente', 'seguridad', 'asalto', 'robo', 'delincuencia',
        'emergencia', 'urgencia'
    ]

    # Palabras clave que indican NO impacto turístico
    NON_TOURIST_KEYWORDS = [
        'economía', 'bolsa', 'mercado', 'dólar',
        'política', 'congreso', 'alcalde',
        'deporte', 'fútbol', 'campeonato',
        'cine', 'entretenimiento',
        'redes sociales', 'social media'
    ]

    # Ubicaciones críticas para turistas
    CRITICAL_LOCATIONS = [
        'cusco',
        'machu picchu',
        'ollantaytambo',
        'aguas calientes',
        'vinicunca',
        'sacred valley'
    ]

    def __init__(self, dedup_hours: int = 6):
        """
        Inicializa el filtro de alertas.
        
        Args:
            dedup_hours: Horas para deduplicación temporal
        """
        self.dedup_hours = dedup_hours
        self.recent_alerts: Dict[str, datetime] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def filter_critical_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra alertas críticas para turistas.
        
        Args:
            alerts: Lista de alertas sin filtrar
            
        Returns:
            List[Dict[str, Any]]: Alertas críticas filtradas
        """
        critical = []
        
        for alert in alerts:
            if self._is_critical_for_tourists(alert):
                if not self._is_duplicate_recent(alert):
                    alert['criticidad'] = self._calculate_criticality(alert)
                    alert['relevancia_turistica'] = 'ALTA'
                    critical.append(alert)
                    self.logger.info(f"Alerta crítica identificada: {alert.get('titulo', 'N/A')}")
                else:
                    self.logger.debug(f"Alerta duplicada (reciente): {alert.get('titulo', 'N/A')}")
        
        return sorted(critical, key=lambda x: x.get('criticidad', 0), reverse=True)

    def _is_critical_for_tourists(self, alert: Dict[str, Any]) -> bool:
        """
        Determina si una alerta es crítica para turistas.
        
        Args:
            alert: Alerta a evaluar
            
        Returns:
            bool: True si es crítica
        """
        text = self._normalize_text(
            alert.get('titulo', '') + " " +
            alert.get('descripcion', '') +
            alert.get('enlace', '')
        )
        
        # Verificar palabras clave negativas primero
        if any(keyword in text for keyword in self.NON_TOURIST_KEYWORDS):
            return False
        
        # Verificar si tiene impacto turístico
        has_tourist_impact = any(
            keyword in text for keyword in self.TOURIST_IMPACT_KEYWORDS
        )
        
        # Verificar ubicación crítica
        in_critical_location = any(
            location in text for location in self.CRITICAL_LOCATIONS
        )
        
        # Verificar urgencia
        urgencia = alert.get('urgencia', '').upper()
        is_urgent = urgencia in ['URGENTE', 'ALTA']
        
        # Es crítica si:
        # 1. Tiene impacto turístico Y urgencia, O
        # 2. Está en ubicación crítica, O
        # 3. Es tipo suspensión/emergencia
        is_suspension = alert.get('tipo', '') in ['SUSPENSION', 'ALERTA', 'EMERGENCIA']
        
        return (has_tourist_impact and is_urgent) or in_critical_location or is_suspension

    def _is_duplicate_recent(self, alert: Dict[str, Any]) -> bool:
        """
        Detecta si la alerta es duplicada dentro del período de deduplicación.
        
        Args:
            alert: Alerta a verificar
            
        Returns:
            bool: True si es duplicada reciente
        """
        alert_key = alert.get('titulo', '') + alert.get('fuente', '')
        
        if alert_key in self.recent_alerts:
            time_diff = datetime.now() - self.recent_alerts[alert_key]
            if time_diff < timedelta(hours=self.dedup_hours):
                return True
        
        self.recent_alerts[alert_key] = datetime.now()
        return False

    def _calculate_criticality(self, alert: Dict[str, Any]) -> float:
        """
        Calcula un score de criticidad (0-100).
        
        Args:
            alert: Alerta a evaluar
            
        Returns:
            float: Score de criticidad
        """
        score = 0.0
        
        # Urgencia (hasta 40 puntos)
        urgencia = alert.get('urgencia', '').upper()
        if urgencia == 'URGENTE':
            score += 40
        elif urgencia == 'ALTA':
            score += 30
        elif urgencia == 'NORMAL':
            score += 10
        
        # Tipo de alerta (hasta 30 puntos)
        tipo = alert.get('tipo', '').upper()
        if tipo in ['SUSPENSION', 'EMERGENCIA']:
            score += 30
        elif tipo == 'ALERTA':
            score += 20
        
        # Ubicación (hasta 20 puntos)
        text = self._normalize_text(
            alert.get('titulo', '') + alert.get('descripcion', '')
        )
        for location in self.CRITICAL_LOCATIONS:
            if location in text:
                score += 20
                break
        
        # Tipo de suspensión (hasta 10 puntos)
        tipo_suspension = alert.get('tipo_suspension', '').upper()
        if tipo_suspension in ['EMERGENCIA', 'CONDICIONES_CLIMATICAS']:
            score += 10
        elif tipo_suspension == 'PARO_LABORAL':
            score += 5
        
        return min(score, 100.0)

    def _normalize_text(self, text: str) -> str:
        """
        Normaliza texto para búsqueda.
        
        Args:
            text: Texto a normalizar
            
        Returns:
            str: Texto normalizado
        """
        return text.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')

    def generate_summary(self, critical_alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera un resumen de alertas críticas.
        
        Args:
            critical_alerts: Alertas críticas filtradas
            
        Returns:
            Dict[str, Any]: Resumen ejecutivo
        """
        summary = {
            'total_alertas_criticas': len(critical_alerts),
            'fecha_generacion': datetime.now().isoformat(),
            'alertas_por_criticidad': {
                'critica': len([a for a in critical_alerts if a.get('criticidad', 0) >= 80]),
                'alta': len([a for a in critical_alerts if 50 <= a.get('criticidad', 0) < 80]),
                'media': len([a for a in critical_alerts if a.get('criticidad', 0) < 50])
            },
            'alertas_por_tipo': {},
            'ubicaciones_afectadas': set(),
            'fuentes': set()
        }
        
        for alert in critical_alerts:
            # Contar por tipo
            tipo = alert.get('tipo', 'OTRO')
            summary['alertas_por_tipo'][tipo] = summary['alertas_por_tipo'].get(tipo, 0) + 1
            
            # Ubicaciones
            if alert.get('ruta_afectada'):
                summary['ubicaciones_afectadas'].add(alert['ruta_afectada'])
            
            # Fuentes
            summary['fuentes'].add(alert.get('fuente', 'Desconocida'))
        
        # Convertir sets a listas
        summary['ubicaciones_afectadas'] = list(summary['ubicaciones_afectadas'])
        summary['fuentes'] = list(summary['fuentes'])
        
        return summary
