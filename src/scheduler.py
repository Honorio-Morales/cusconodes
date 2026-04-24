"""
Scheduler - Ejecutor de tareas programadas del sistema CuscoNodes
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class CuscoNodesScheduler:
    """
    Orquestador de scraping y filtrado con ejecución programada.
    
    Flujo:
    1. Ejecutar todos los scrapers
    2. Agregar metadatos de tiempo
    3. Guardar datos raw
    4. Filtrar alertas críticas
    5. Generar resumen
    6. Guardar datos procesados
    """

    def __init__(self, data_path: str = './data'):
        """
        Inicializa el scheduler.
        
        Args:
            data_path: Ruta base para almacenamiento de datos
        """
        self.data_path = data_path
        self.raw_path = os.path.join(data_path, 'raw')
        self.processed_path = os.path.join(data_path, 'processed')
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Crear directorios si no existen
        Path(self.raw_path).mkdir(parents=True, exist_ok=True)
        Path(self.processed_path).mkdir(parents=True, exist_ok=True)

    def run_full_pipeline(self, scrapers: List[Any], alert_filter: Any = None) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo de scraping → filtrado → guardado.
        
        Args:
            scrapers: Lista de instancias de scrapers a ejecutar
            alert_filter: Filtrador de alertas críticas
            
        Returns:
            Dict[str, Any]: Resultado de la ejecución
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'scrapers_executed': [],
            'total_alerts_raw': 0,
            'total_alerts_critical': 0,
            'files_created': []
        }
        
        try:
            # Paso 1: Ejecutar todos los scrapers
            self.logger.info("="*60)
            self.logger.info("Iniciando pipeline completo de CuscoNodes")
            self.logger.info("="*60)
            
            all_alerts = []
            
            for scraper in scrapers:
                try:
                    self.logger.info(f"\n📡 Ejecutando: {scraper.name}")
                    alerts = scraper.scrape()
                    
                    if alerts:
                        all_alerts.extend(alerts)
                        
                        # Guardar datos raw por scraper
                        raw_file = self._save_raw_data(scraper.name, alerts)
                        result['files_created'].append(raw_file)
                        
                        self.logger.info(f"✅ {len(alerts)} registros extraídos de {scraper.name}")
                    else:
                        self.logger.warning(f"⚠️  No se obtuvieron datos de {scraper.name}")
                    
                    result['scrapers_executed'].append({
                        'name': scraper.name,
                        'status': 'success',
                        'records': len(alerts)
                    })
                    
                except Exception as e:
                    self.logger.error(f"❌ Error en {scraper.name}: {e}")
                    result['scrapers_executed'].append({
                        'name': scraper.name,
                        'status': 'error',
                        'error': str(e)
                    })
            
            result['total_alerts_raw'] = len(all_alerts)
            self.logger.info(f"\n📊 Total de alertas extraídas: {len(all_alerts)}")
            
            # Paso 2: Filtrar alertas críticas
            critical_alerts = all_alerts
            if alert_filter:
                self.logger.info("\n🔍 Filtrando alertas críticas...")
                critical_alerts = alert_filter.filter_critical_alerts(all_alerts)
                result['total_alerts_critical'] = len(critical_alerts)
                self.logger.info(f"✅ Alertas críticas identificadas: {len(critical_alerts)}")
            
            # Paso 3: Guardar datos procesados
            if critical_alerts:
                processed_file = self._save_processed_data(critical_alerts)
                result['files_created'].append(processed_file)
            
            # Paso 4: Generar resumen
            if alert_filter:
                summary = alert_filter.generate_summary(critical_alerts)
                summary_file = self._save_summary(summary)
                result['files_created'].append(summary_file)
                self.logger.info(f"\n📋 Resumen guardado en {summary_file}")
            
            self.logger.info("\n" + "="*60)
            self.logger.info("✅ Pipeline completado exitosamente")
            self.logger.info("="*60 + "\n")
            
        except Exception as e:
            self.logger.error(f"❌ Error crítico en pipeline: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result

    def _save_raw_data(self, scraper_name: str, data: List[Dict[str, Any]]) -> str:
        """
        Guarda datos raw en archivo JSON.
        
        Args:
            scraper_name: Nombre del scraper
            data: Datos a guardar
            
        Returns:
            str: Ruta del archivo creado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"alertas_{scraper_name.lower().replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(self.raw_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Datos guardados en {filepath}")
        except Exception as e:
            self.logger.error(f"Error guardando datos raw: {e}")
        
        return filepath

    def _save_processed_data(self, critical_alerts: List[Dict[str, Any]]) -> str:
        """
        Guarda alertas procesadas/filtradas.
        
        Args:
            critical_alerts: Alertas críticas filtradas
            
        Returns:
            str: Ruta del archivo creado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"alertas_criticas_{timestamp}.json"
        filepath = os.path.join(self.processed_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(critical_alerts, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Alertas críticas guardadas en {filepath}")
        except Exception as e:
            self.logger.error(f"Error guardando alertas procesadas: {e}")
        
        return filepath

    def _save_summary(self, summary: Dict[str, Any]) -> str:
        """
        Guarda resumen ejecutivo de alertas.
        
        Args:
            summary: Resumen a guardar
            
        Returns:
            str: Ruta del archivo creado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"resumen_alertas_{timestamp}.json"
        filepath = os.path.join(self.processed_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Resumen guardado en {filepath}")
        except Exception as e:
            self.logger.error(f"Error guardando resumen: {e}")
        
        return filepath

    def get_latest_critical_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene las últimas alertas críticas procesadas.
        
        Args:
            limit: Número máximo de alertas a retornar
            
        Returns:
            List[Dict[str, Any]]: Alertas más recientes
        """
        try:
            # Buscar el archivo de alertas críticas más reciente
            processed_files = sorted(
                Path(self.processed_path).glob('alertas_criticas_*.json'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            if not processed_files:
                self.logger.warning("No hay alertas críticas procesadas")
                return []
            
            latest_file = processed_files[0]
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            
            return alerts[:limit]
            
        except Exception as e:
            self.logger.error(f"Error obteniendo alertas recientes: {e}")
            return []
