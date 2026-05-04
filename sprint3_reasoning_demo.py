#!/usr/bin/env python3
"""
Sprint 3 Demo - Razonamiento con datos reales de Sprint 2

Carga alertas reales del Sprint 2 y demuestra el agente de razonamiento.
"""

import sys
import os
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reasoning_agent_lite import ReasoningPipelineLite
from datetime import datetime


def demo_reasoning_with_real_data():
    """Demuestra el agente de razonamiento con datos reales de Sprint 2."""
    
    print("\n" + "="*70)
    print("🚀 CUSCONODES - SPRINT 3 DEMO")
    print("Agente de Razonamiento con Datos Reales Sprint 2")
    print("="*70 + "\n")
    
    # Cargar datos reales de Sprint 2
    raw_path = './data/raw'
    
    if not os.path.exists(raw_path):
        logger.error(f"❌ Carpeta {raw_path} no encontrada")
        return
    
    # Buscar archivos JSON
    json_files = [f for f in os.listdir(raw_path) if f.endswith('.json')]
    
    if not json_files:
        logger.error(f"❌ No hay archivos JSON en {raw_path}")
        return
    
    logger.info(f"📁 Encontrados {len(json_files)} archivos de datos\n")
    
    # Cargar todas las alertas
    all_alerts = []
    for json_file in json_files:
        filepath = os.path.join(raw_path, json_file)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_alerts.extend(data)
                    logger.info(f"   ✅ {json_file}: {len(data)} registros cargados")
                else:
                    logger.warning(f"   ⚠️  {json_file}: Formato no soportado")
        except Exception as e:
            logger.error(f"   ❌ Error cargando {json_file}: {e}")
    
    if not all_alerts:
        logger.error("❌ No se cargaron alertas")
        return
    
    logger.info(f"\n📊 Total de alertas cargadas: {len(all_alerts)}\n")
    
    # Ejecutar razonamiento
    print("-" * 70)
    reasoning_pipeline = ReasoningPipelineLite(data_path='./data')
    classified_alerts = reasoning_pipeline.process_raw_alerts(all_alerts)
    print("-" * 70 + "\n")
    
    # Mostrar resultados
    print_detailed_results(classified_alerts)
    
    # Guardar clasificadas
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join('./data/processed', f'alertas_clasificadas_demo_{timestamp}.json')
    
    os.makedirs('./data/processed', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classified_alerts, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n✅ Resultados guardados en: {output_file}\n")
    
    print("\n" + "="*70)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("="*70 + "\n")


def print_detailed_results(classified_alerts):
    """Imprime resultados detallados."""
    
    # Separar por categoría
    criticas = [a for a in classified_alerts if a.get('clasificacion') == 'CRÍTICA']
    informativas = [a for a in classified_alerts if a.get('clasificacion') == 'INFORMATIVA']
    irrelevantes = [a for a in classified_alerts if a.get('clasificacion') == 'IRRELEVANTE']
    
    print(f"\n🎯 RESULTADOS DE CLASIFICACIÓN:\n")
    print(f"  🚨 CRÍTICA: {len(criticas)} alertas ({len(criticas)*100//len(classified_alerts) if classified_alerts else 0}%)")
    print(f"  ℹ️  INFORMATIVA: {len(informativas)} alertas ({len(informativas)*100//len(classified_alerts) if classified_alerts else 0}%)")
    print(f"  ✅ IRRELEVANTE: {len(irrelevantes)} alertas ({len(irrelevantes)*100//len(classified_alerts) if classified_alerts else 0}%)")
    
    # Mostrar alertas críticas
    if criticas:
        print(f"\n" + "-"*70)
        print(f"🚨 ALERTAS CRÍTICAS ({len(criticas)}):\n")
        for i, alert in enumerate(criticas[:5], 1):  # Mostrar máximo 5
            print(f"  {i}. {alert.get('titulo', '')[:60]}")
            print(f"     Fuente: {alert.get('fuente', '')}")
            print(f"     Confianza: {alert.get('confianza', 0)}%")
            if alert.get('ubicaciones'):
                print(f"     Ubicaciones: {', '.join(alert['ubicaciones'])}")
            print(f"     Tipo: {alert.get('tipo_evento', '')}")
            print(f"     Acción: {alert.get('recomendacion', '')}\n")
        if len(criticas) > 5:
            print(f"  ... y {len(criticas) - 5} más\n")
    
    # Mostrar informativas (sample)
    if informativas:
        print(f"-"*70)
        print(f"ℹ️  ALERTAS INFORMATIVAS (muestra de {min(3, len(informativas))}):\n")
        for alert in informativas[:3]:
            print(f"  • {alert.get('titulo', '')[:60]}")
            print(f"    ({alert.get('fuente', '')})\n")
    
    # Estadísticas por fuente
    fuentes = {}
    for alert in classified_alerts:
        fuente = alert.get('fuente', 'Desconocida')
        if fuente not in fuentes:
            fuentes[fuente] = {'total': 0, 'critica': 0}
        fuentes[fuente]['total'] += 1
        if alert.get('clasificacion') == 'CRÍTICA':
            fuentes[fuente]['critica'] += 1
    
    print(f"-"*70)
    print(f"📊 ESTADÍSTICAS POR FUENTE:\n")
    for fuente, stats in sorted(fuentes.items()):
        pct = stats['critica'] * 100 // stats['total'] if stats['total'] > 0 else 0
        print(f"  {fuente}: {stats['total']} total, {stats['critica']} críticas ({pct}%)")
    
    print()


if __name__ == '__main__':
    demo_reasoning_with_real_data()
