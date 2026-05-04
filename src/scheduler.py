"""
Scheduler - Ejecutor de tareas programadas del sistema CuscoNodes
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
import json
import os
from pathlib import Path

# Sprint 3: Importar agente de razonamiento
try:
    from src.reasoning_agent_lite import ReasoningPipelineLite as ReasoningPipeline
    REASONING_AVAILABLE = True
except ImportError:
    try:
        from src.reasoning_agent import ReasoningPipeline
        REASONING_AVAILABLE = True
    except ImportError:
        REASONING_AVAILABLE = False

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
            
            # Paso 2: RAZONAMIENTO (Sprint 3) - Usar agente IA si disponible
            classified_alerts = all_alerts
            if REASONING_AVAILABLE and all_alerts:
                try:
                    reasoning_pipeline = ReasoningPipeline(self.data_path)
                    classified_alerts = reasoning_pipeline.process_raw_alerts(all_alerts)
                    result['reasoning_applied'] = True
                    result['total_alerts_critical'] = sum(
                        1 for a in classified_alerts if a.get('clasificacion') == 'CRÍTICA'
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️  Razonamiento no disponible, usando alertas raw: {e}")
                    result['reasoning_applied'] = False
            else:
                result['reasoning_applied'] = False
                # Fallback a filtrado simple si razonamiento no disponible
                if alert_filter:
                    self.logger.info("\n🔍 Filtrando alertas críticas (modo legacy)...")
                    classified_alerts = alert_filter.filter_critical_alerts(all_alerts)
                    result['total_alerts_critical'] = len(classified_alerts)
            
            # Paso 3: Guardar datos procesados/clasificados
            processed_file = None
            if classified_alerts:
                processed_file = self._save_processed_data(classified_alerts, use_reasoning=result['reasoning_applied'])
                result['files_created'].append(processed_file)
                self.logger.info(f"✅ Alertas procesadas guardadas: {len(classified_alerts)}")
            
            # Paso 4: Generar resumen
            if alert_filter and not result['reasoning_applied']:
                summary = alert_filter.generate_summary(classified_alerts)
                summary_file = self._save_summary(summary)
                result['files_created'].append(summary_file)
                self.logger.info(f"\n📋 Resumen guardado en {summary_file}")
            elif result['reasoning_applied']:
                # Generar resumen desde alertas clasificadas
                summary = self._generate_reasoning_summary(classified_alerts)
                summary_file = self._save_summary(summary)
                result['files_created'].append(summary_file)
                self.logger.info(f"\n📋 Resumen IA guardado en {summary_file}")
            
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

    def _save_processed_data(self, critical_alerts: List[Dict[str, Any]], use_reasoning: bool = False) -> str:
        """
        Guarda alertas procesadas/filtradas.
        
        Args:
            critical_alerts: Alertas críticas filtradas o clasificadas
            use_reasoning: Si True, usa nombre para alertas clasificadas (IA)
            
        Returns:
            str: Ruta del archivo creado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Usar nombre diferente si fueron clasificadas con IA
        if use_reasoning:
            filename = f"alertas_clasificadas_{timestamp}.json"
        else:
            filename = f"alertas_criticas_{timestamp}.json"
        
        filepath = os.path.join(self.processed_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(critical_alerts, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Alertas guardadas en {filepath}")
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

    def _generate_reasoning_summary(self, classified_alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera resumen ejecutivo desde alertas clasificadas por IA.
        
        Args:
            classified_alerts: Alertas clasificadas por razonamiento
            
        Returns:
            Dict con resumen ejecutivo
        """
        critica = [a for a in classified_alerts if a.get('clasificacion') == 'CRÍTICA']
        informativa = [a for a in classified_alerts if a.get('clasificacion') == 'INFORMATIVA']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_alertas': len(classified_alerts),
            'alertas_criticas': len(critica),
            'alertas_informativas': len(informativa),
            'fuentes': list(set(a.get('fuente', 'Desconocida') for a in classified_alerts)),
            'alertas_criticas_lista': [
                {
                    'titulo': a['titulo'],
                    'fuente': a['fuente'],
                    'ubicaciones': a.get('ubicaciones', []),
                    'recomendacion': a.get('recomendacion', 'Notificar')
                }
                for a in critica[:5]  # Top 5
            ],
            'nota': 'Generado por Agente de Razonamiento (Sprint 3)'
        }

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
