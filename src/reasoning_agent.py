"""
Reasoning Agent - Agente de Razonamiento (Sprint 3)

Clasifica alertas por urgencia usando transformers (zero-shot classification).
Etapa 2 del pipeline agéntico: Percepción → Razonamiento → Acción
"""

import logging
from typing import Dict, List, Any
from transformers import pipeline
import re

logger = logging.getLogger(__name__)


class ReasoningAgent:
    """
    Agente que entiende y clasifica alertas turísticas.
    
    Usa zero-shot classification para determinar:
    - CRÍTICA: Impacta directamente al turista (cierre de rutas, huelgas)
    - INFORMATIVA: Útil pero no urgente (eventos culturales)
    - IRRELEVANTE: Sin impacto turístico
    """

    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        """
        Inicializa el agente de razonamiento.
        
        Args:
            model_name: Modelo de transformers para clasificación
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = model_name
        
        self.logger.info(f"⏳ Cargando modelo: {model_name}...")
        try:
            # Cargador de pipeline para zero-shot classification
            self.classifier = pipeline(
                "zero-shot-classification",
                model=model_name,
                device=-1  # CPU (cambiar a 0 si tienes GPU)
            )
            self.logger.info("✅ Modelo cargado exitosamente")
        except Exception as e:
            self.logger.error(f"❌ Error cargando modelo: {e}")
            raise

        # Palabras clave y contexto turístico
        self.critical_keywords = {
            "cierre", "huelga", "suspensión", "bloqueado", "bloqueo",
            "paro", "cortado", "vía cortada", "carretera cerrada",
            "evacuación", "peligro", "urgente", "alerta", "tormenta",
            "lluvia extrema", "derrumbe", "inundación", "avalancha"
        }
        
        self.tourism_locations = {
            "machu picchu", "ollantaytambo", "cusco", "valle sagrado",
            "plaza de armas", "inca trail", "sacsayhuamán", "aguas calientes",
            "cusco airport", "perurail", "incarail", "tren"
        }

    def classify_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clasifica una alerta individual.
        
        Args:
            alert: Diccionario con título, descripción, fuente, etc.
            
        Returns:
            Dict con clasificación, confianza, ubicaciones, recomendación
        """
        try:
            # Combinar título y descripción para clasificar
            titulo = alert.get('titulo', '').lower()
            descripcion = alert.get('descripcion', alert.get('enlace', '')).lower()
            
            texto_completo = f"{titulo} {descripcion}"
            
            # Detectar ubicaciones turísticas
            ubicaciones = self._detect_locations(texto_completo)
            
            # Detectar si tiene palabras clave críticas
            tiene_critica_keyword = any(kw in texto_completo for kw in self.critical_keywords)
            
            # Clasificar con modelo
            candidatos = ["CRÍTICA", "INFORMATIVA", "IRRELEVANTE"]
            resultado = self.classifier(
                texto_completo[:512],  # Limitar a 512 caracteres por modelo
                candidatos,
                multi_class=False
            )
            
            clasificacion = resultado['labels'][0]
            confianza = int(resultado['scores'][0] * 100)
            
            # Booster: si tiene keywords críticas y ubicaciones, elevar a CRÍTICA
            if tiene_critica_keyword and ubicaciones:
                if confianza < 70:
                    clasificacion = "CRÍTICA"
                    confianza = min(95, confianza + 20)
            
            # Detectar tipo de evento
            tipo_evento = self._detect_event_type(texto_completo)
            
            # Generar recomendación para agencia
            recomendacion = self._generate_recommendation(clasificacion, ubicaciones, tipo_evento)
            
            return {
                "id": alert.get('id'),
                "titulo": alert.get('titulo', 'Sin título'),
                "fuente": alert.get('fuente', 'Desconocida'),
                "enlace": alert.get('enlace', ''),
                
                # Clasificación (Sprint 3)
                "clasificacion": clasificacion,
                "confianza": confianza,
                "ubicaciones": ubicaciones,
                "tipo_evento": tipo_evento,
                
                # Generado por IA
                "resumen_ia": self._generate_summary(titulo, clasificacion),
                "recomendacion": recomendacion,
                
                # Metadatos originales
                "fecha_scrape": alert.get('fecha_scrape', ''),
                "fuente_original": alert.get('fuente', ''),
                "tipo": alert.get('tipo', 'alerta'),
                
                # Score para ordenamiento
                "score_urgencia": self._calculate_urgency_score(clasificacion, confianza)
            }
        
        except Exception as e:
            self.logger.error(f"Error clasificando alerta: {e}")
            # Retornar clasificación segura en caso de error
            return {
                "id": alert.get('id'),
                "titulo": alert.get('titulo', ''),
                "fuente": alert.get('fuente', ''),
                "clasificacion": "INFORMATIVA",  # Default seguro
                "confianza": 50,
                "error": str(e)
            }

    def classify_batch(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clasifica múltiples alertas.
        
        Args:
            alerts: Lista de alertas a clasificar
            
        Returns:
            Lista de alertas clasificadas
        """
        self.logger.info(f"🔄 Clasificando {len(alerts)} alertas...")
        
        clasificadas = []
        for i, alert in enumerate(alerts):
            try:
                result = self.classify_alert(alert)
                clasificadas.append(result)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"   ✅ {i + 1}/{len(alerts)} procesadas")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Error en alerta {i+1}: {e}")
                continue
        
        self.logger.info(f"✅ Clasificación completada: {len(clasificadas)} alertas procesadas")
        return clasificadas

    def _detect_locations(self, texto: str) -> List[str]:
        """Detecta ubicaciones turísticas mencionadas."""
        ubicaciones_encontradas = []
        for loc in self.tourism_locations:
            if loc in texto:
                ubicaciones_encontradas.append(loc.title())
        return list(set(ubicaciones_encontradas))  # Remover duplicados

    def _detect_event_type(self, texto: str) -> str:
        """Detecta el tipo de evento."""
        if any(kw in texto for kw in ["huelga", "paro", "protesta"]):
            return "protesta_social"
        elif any(kw in texto for kw in ["cierre", "suspensión", "bloqueado"]):
            return "cierre_transporte"
        elif any(kw in texto for kw in ["lluvia", "tormenta", "nieve", "derrumbe"]):
            return "fenomeno_natural"
        elif any(kw in texto for kw in ["evento", "festival", "inti raymi"]):
            return "evento_cultural"
        elif any(kw in texto for kw in ["restricción", "entrada", "ticket"]):
            return "restriccion_acceso"
        else:
            return "otro"

    def _generate_summary(self, titulo: str, clasificacion: str) -> str:
        """Genera un resumen contextual."""
        if clasificacion == "CRÍTICA":
            return f"⚠️ ALERTA CRÍTICA: {titulo[:80]}"
        elif clasificacion == "INFORMATIVA":
            return f"ℹ️ Información: {titulo[:80]}"
        else:
            return titulo[:80]

    def _generate_recommendation(self, clasificacion: str, ubicaciones: List[str], tipo_evento: str) -> str:
        """Genera recomendación para la agencia."""
        if clasificacion == "CRÍTICA":
            if ubicaciones:
                return f"Notificar INMEDIATAMENTE a turistas en {', '.join(ubicaciones)}"
            else:
                return "Notificar INMEDIATAMENTE a todos los turistas activos"
        elif clasificacion == "INFORMATIVA":
            return "Compartir como información general con turistas interesados"
        else:
            return "No requiere notificación"

    def _calculate_urgency_score(self, clasificacion: str, confianza: int) -> int:
        """Calcula score de urgencia (0-100) para ordenamiento."""
        scores = {
            "CRÍTICA": 90,
            "INFORMATIVA": 50,
            "IRRELEVANTE": 10
        }
        base_score = scores.get(clasificacion, 50)
        
        # Ajustar por confianza
        adjusted_score = int(base_score * (confianza / 100))
        return min(100, adjusted_score)


class ReasoningPipeline:
    """
    Pipeline completo: Percepción → Razonamiento → Almacenamiento
    """
    
    def __init__(self, data_path: str = './data'):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data_path = data_path
        self.reasoning_agent = ReasoningAgent()
    
    def process_raw_alerts(self, raw_alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa alertas raw con el agente de razonamiento.
        
        Args:
            raw_alerts: Alertas sin procesar de los scrapers
            
        Returns:
            Alertas clasificadas y procesadas
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("🧠 ETAPA 2: RAZONAMIENTO (Motor IA Local)")
        self.logger.info("="*60)
        
        # Enriquecer alertas con ID si no lo tienen
        for i, alert in enumerate(raw_alerts):
            if 'id' not in alert:
                alert['id'] = i + 1
        
        # Clasificar con agente
        classified_alerts = self.reasoning_agent.classify_batch(raw_alerts)
        
        # Estadísticas
        stats = self._calculate_stats(classified_alerts)
        self.logger.info(f"\n📊 Estadísticas de Clasificación:")
        self.logger.info(f"   CRÍTICA: {stats['critica']} ({stats['critica_pct']:.1f}%)")
        self.logger.info(f"   INFORMATIVA: {stats['informativa']} ({stats['informativa_pct']:.1f}%)")
        self.logger.info(f"   IRRELEVANTE: {stats['irrelevante']} ({stats['irrelevante_pct']:.1f}%)")
        
        return classified_alerts
    
    def _calculate_stats(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estadísticas de clasificación."""
        total = len(alerts)
        critica = sum(1 for a in alerts if a.get('clasificacion') == 'CRÍTICA')
        informativa = sum(1 for a in alerts if a.get('clasificacion') == 'INFORMATIVA')
        irrelevante = sum(1 for a in alerts if a.get('clasificacion') == 'IRRELEVANTE')
        
        return {
            'critica': critica,
            'informativa': informativa,
            'irrelevante': irrelevante,
            'critica_pct': (critica / total * 100) if total > 0 else 0,
            'informativa_pct': (informativa / total * 100) if total > 0 else 0,
            'irrelevante_pct': (irrelevante / total * 100) if total > 0 else 0
        }
